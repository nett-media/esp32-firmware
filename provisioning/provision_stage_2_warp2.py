#!/usr/bin/python3 -u

import contextlib
from contextlib import contextmanager
import datetime
import getpass
import io
import json
import os
import re
import secrets
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import csv
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from tinkerforge.ip_connection import IPConnection, base58encode, base58decode, BASE58
from tinkerforge.bricklet_rgb_led_v2 import BrickletRGBLEDV2

from provision_common.provision_common import *
from provision_common.bricklet_evse_v2 import BrickletEVSEV2
from provision_stage_3_warp2 import Stage3

evse = None

def run_bricklet_tests(ipcon, result, qr_variant, qr_power, ssid, stage3):
    global evse
    enumerations = enumerate_devices(ipcon)

    master = next((e for e in enumerations if e.device_identifier == 13), None)
    evse_enum = next((e for e in enumerations if e.device_identifier == 2167), None)

    if qr_variant != "B" and len(enumerations) not in [1, 2]:
        fatal_error("Unexpected number of devices! Expected 1 or 2 but got {}.".format(len(enumerations)))

    if evse_enum is None:
        fatal_error("No EVSE Bricklet found!")

    is_basic = master is not None

    evse = BrickletEVSEV2(evse_enum.uid, ipcon)
    has_meter = evse.get_energy_meter_state().available

    is_smart = not is_basic and not has_meter
    is_pro = not is_basic and has_meter

    d = {"P": "Pro", "S": "Smart", "B": "Basic"}

    if is_basic and qr_variant != "B":
        fatal_error("Scanned QR code implies variant {}, but detected was Basic (i.e. an Master Brick was found)".format(d[qr_variant]))

    if is_smart and qr_variant != "S":
        fatal_error("Scanned QR code implies variant {}, but detected was Smart: An ESP32 Brick was found, but no energy meter. Is the meter not connected or the display not lighting up? Is the QR code correct?".format(d[qr_variant]))

    if is_pro and qr_variant != "P":
        fatal_error("Scanned QR code implies variant {}, but detected was Pro: An ESP32 Brick and an energy meter was found. Is the QR code correct?".format(d[qr_variant]))

    result["evse_uid"] = evse_enum.uid
    print("EVSE UID is {}".format(evse_enum.uid))

    if is_basic:
        result["master_uid"] = master.uid
        print("Master UID is {}".format(master.uid))

    jumper_config, has_lock_switch = evse.get_hardware_configuration()

    if qr_power == "11" and jumper_config != 3:
        fatal_error("Wrong jumper config detected: {} but expected {} as the configured power is {} kW.".format(jumper_config, 3, qr_power))

    if qr_power == "22" and jumper_config != 6:
        fatal_error("Wrong jumper config detected: {} but expected {} as the configured power is {} kW.".format(jumper_config, 6, qr_power))

    result["jumper_config_checked"] = True
    if has_lock_switch:
        fatal_error("Wallbox has lock switch. Is the diode missing?")

    result["diode_checked"] = True

    _configured, _incoming, outgoing, _managed = evse.get_max_charging_current()
    if qr_power == "11" and outgoing != 20000:
        fatal_error("Wrong type 2 cable config detected: Allowed current is {} but expected 20 A, as this is a 11 kW box.".format(outgoing / 1000))
    if qr_power == "22" and outgoing != 32000:
        fatal_error("Wrong type 2 cable config detected: Allowed current is {} but expected 32 A, as this is a 22 kW box.".format(outgoing / 1000))

    result["resistor_checked"] = True

    if is_pro:
        meter_str = urllib.request.urlopen('http://{}/meter/live'.format(ssid), timeout=3).read()
        meter_data = json.loads(meter_str)
        sps = meter_data["samples_per_second"]
        samples = meter_data["samples"]
        if not 0.2 < sps < 2.5:
            fatal_error("Expected between 0.2 and 2.5 energy meter samples per second, but got {}".format(sps))
        if len(samples) < 2:
            fatal_error("Expected at least 10 samples but got {}".format(len(samples)))

        error_count = evse.get_energy_meter_state().error_count
        if any(x != 0 for x in error_count):
            fatal_error("Energy meter error count is {}, expected only zeros!".format(error_count))

        result["energy_meter_reachable"] = True

    stage3.test_front_panel_button()
    result["front_panel_button_tested"] = True

    if is_smart or is_pro:
        nfc_str = urllib.request.urlopen('http://{}/nfc/seen_tags'.format(ssid), timeout=3).read()
        nfc_data = json.loads(nfc_str)

        if nfc_data[0]['tag_type'] != 2 or \
           nfc_data[0]['tag_id'] != [0x04, 0xBA, 0x38, 0x42, 0xEF, 0x6C, 0x80] or \
           nfc_data[0]['last_seen'] > 100:
            fatal_error("Did not find NFC tag: {}".format(nfc_str))


def exists_evse_test_report(evse_uid):
    with open(os.path.join("evse_v2_test_report", "full_test_log.csv"), newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if row[0] == evse_uid:
                return True
    return False


def is_front_panel_button_pressed():
    global evse
    return evse.get_low_level_state().gpio[6]

def get_iec_state():
    global evse
    return chr(ord('A') + evse.get_state().iec61851_state)

def reset_dc_fault():
    global evse
    return evse.reset_dc_fault_current(0xDC42FA23)

def has_evse_error():
    global evse
    return evse.get_state().error_state != 0

def led_wrap():
    stage3 = Stage3(is_front_panel_button_pressed_function=is_front_panel_button_pressed, get_iec_state_function=get_iec_state, reset_dc_fault_function=reset_dc_fault, has_evse_error_function=has_evse_error)
    stage3.setup()
    stage3.set_led_strip_color((0, 0, 255))
    try:
        main(stage3)
    except BaseException:
        stage3.power_off()
        stage3.set_led_strip_color((255, 0, 0))
        stage3.beep_failure()
        raise
    else:
        stage3.power_off()
        stage3.set_led_strip_color((0, 255, 0))
        stage3.beep_success()

blink_start = None
blink_count = 0
def start_blink(count):
    global blink_start, blink_count
    assert count in [3, 2, 1, 0], count
    blink_start = time.monotonic()
    blink_count = count

def blink_tick(stage3):
    diff = (time.monotonic() - blink_start)
    diff -= int(diff)
    color = (255, 127, 0) if diff <= 0.5 else (0, 0, 0)
    if blink_count >= 3:
        stage3.set_led_strip_color(color)
    elif blink_count == 2:
        stage3.set_led_strip_color((0, 0, 255), color)
    elif blink_count == 1:
        stage3.set_led_strip_color((0, 0, 255), (0, 0, 255), color)
    else:
        stage3.set_led_strip_color((0, 0, 255))

def stop_blink(stage3):
    global blink_start, blink_count
    blink_start = None
    blink_count = 0
    stage3.set_led_strip_color((0, 0, 255))

class ContentTypeRemover(urllib.request.BaseHandler):
    def http_request(self, req):
        if req.has_header('Content-type'):
            req.remove_header('Content-type')
        return req
    https_request = http_request

def main(stage3):
    result = {"start": now()}

    with ChangedDirectory(os.path.join("..", "..", "firmwares")):
        run(["git", "pull"])

    evse_directory = os.path.join("..", "..", "firmwares", "bricklets", "evse_v2")
    evse_path = os.readlink(os.path.join(evse_directory, "bricklet_evse_v2_firmware_latest.zbin"))
    evse_path = os.path.join(evse_directory, evse_path)

    firmware_directory = os.path.join("..", "..", "firmwares", "bricks", "warp2_charger")
    firmware_path = os.readlink(os.path.join(firmware_directory, "brick_warp2_charger_firmware_latest.bin"))
    firmware_path = os.path.join(firmware_directory, firmware_path)

    #T:WARP2-CP-22KW-50;V:2.1;S:5000000001;B:2021-09;O:SO/2020123;I:17/42;E:1;C:0;;;;;;
    pattern = r'^T:WARP2-C(B|S|P)-(11|22)KW-(50|75);V:(\d+\.\d+);S:(5\d{9});B:(\d{4}-\d{2});O:(SO/B?[0-9]+);I:(\d+/\d+);E:(\d+);C:([01]);;;*$'
    qr_code = my_input("Scan the docket QR code")
    match = re.match(pattern, qr_code)
    while not match:
        qr_code = my_input("Scan the docket QR code", red)
        match = re.match(pattern, qr_code)

    docket_variant = match.group(1)
    docket_power = match.group(2)
    docket_cable_len = match.group(3)
    docket_hw_version = match.group(4)
    docket_serial = match.group(5)
    docket_built = match.group(6)
    docket_order = match.group(7)
    docket_item = match.group(8)
    docket_supply_cable_extension = int(match.group(9))
    docket_has_cee = match.group(10) == "1"

    print("Docket QR code data:")
    print("    WARP Charger {}".format({"B": "Basic", "S": "Smart", "P": "Pro"}[docket_variant]))
    print("    {} kW".format(docket_power))
    print("    {:1.1f} m".format(int(docket_cable_len) / 10.0))
    print("    CEE: {}".format("Yes" if docket_has_cee else "No"))
    print("    HW Version: {}".format(docket_hw_version))
    print("    Serial: {}".format(docket_serial))
    print("    Build month: {}".format(docket_built))
    print("    Order: {}".format(docket_order))
    print("    Item: {}".format(docket_item))
    print("    Supply Cable Extension: {}".format(docket_supply_cable_extension))

    result["order"] = docket_order
    result["order_item"] = docket_item
    result["supply_cable_extension"] = docket_supply_cable_extension
    result["docket_qr_code"] = match.group(0)

    #T:WARP2-CP-22KW-50;V:2.1;S:5000000001;B:2021-09;;
    pattern = r'^T:WARP2-C(B|S|P)-(11|22)KW-(50|75);V:(\d+\.\d+);S:(5\d{9});B:(\d{4}-\d{2});;;*$'
    qr_code = my_input("Scan the wallbox QR code")
    match = re.match(pattern, qr_code)
    while not match:
        qr_code = my_input("Scan the wallbox QR code", red)
        match = re.match(pattern, qr_code)

    qr_variant = match.group(1)
    qr_power = match.group(2)
    qr_cable_len = match.group(3)
    qr_hw_version = match.group(4)
    qr_serial = match.group(5)
    qr_built = match.group(6)

    if docket_variant != qr_variant or \
       docket_power != qr_power or \
       docket_cable_len != qr_cable_len or \
       docket_hw_version != qr_hw_version or \
       docket_serial != qr_serial or \
       docket_built != qr_built:
        fatal_error("Docket and wallbox QR code do not match!")

    print("Wallbox QR code data:")
    print("    WARP Charger {}".format({"B": "Basic", "S": "Smart", "P": "Pro"}[qr_variant]))
    print("    {} kW".format(qr_power))
    print("    {:1.1f} m".format(int(qr_cable_len) / 10.0))
    print("    HW Version: {}".format(qr_hw_version))
    print("    Serial: {}".format(qr_serial))
    print("    Build month: {}".format(qr_built))

    result["serial"] = qr_serial
    result["qr_code"] = match.group(0)

    if qr_variant != "B":
        pattern = r"^WIFI:S:(esp32|warp|warp2)-([{BASE58}]{{3,6}});T:WPA;P:([{BASE58}]{{4}}-[{BASE58}]{{4}}-[{BASE58}]{{4}}-[{BASE58}]{{4}});;$".format(BASE58=BASE58)
        qr_code = getpass.getpass(green("Scan the ESP Brick QR code"))
        match = re.match(pattern, qr_code)
        while not match:
            qr_code = getpass.getpass(red("Scan the ESP Brick QR code"))
            match = re.match(pattern, qr_code)

        if docket_supply_cable_extension != 0 or docket_has_cee:
            stage3.power_on('CEE')
        else:
            stage3.power_on({"B": "Basic", "S": "Smart", "P": "Pro"}[qr_variant])

        hardware_type = match.group(1)
        esp_uid_qr = match.group(2)
        passphrase_qr = match.group(3)

        print("ESP Brick QR code data:")
        print("    Hardware type: {}".format(hardware_type))
        print("    UID: {}".format(esp_uid_qr))

        print(green("Waiting for NFC tags"), end="")
        seen_tags = []
        last_len = 0
        start_blink(3)
        while len(seen_tags) < 3:
            seen_tags = [x for x in stage3.get_nfc_tag_ids() if any(y != 0 for y in x.tag_id)]
            if len(seen_tags) != last_len:
                if len(seen_tags) == 0:
                    start_blink(3)
                elif len(seen_tags) == 1:
                    start_blink(2)
                elif len(seen_tags) == 2:
                    start_blink(1)
                else:
                    start_blink(0)
                last_len = len(seen_tags)
            print(green("\rWaiting for NFC tags. {} seen".format(len(seen_tags))), end="")
            blink_tick(stage3)
            time.sleep(0.1)
        stop_blink(stage3)
        print("\r3 NFC tags seen." + " " * 20)

        result["uid"] = esp_uid_qr

        ssid = "warp2-" + esp_uid_qr

        print("Connecting via ethernet to {}".format(ssid), end="")

        for i in range(30):
            start = time.monotonic()
            try:
                with urllib.request.urlopen("http://{}/event_log".format(ssid), timeout=1) as f:
                    event_log = f.read().decode('utf-8')
                    break
            except:
                pass
            t = max(0, 1 - (time.monotonic() - start))
            time.sleep(t)
            print(".", end="")
        else:
            fatal_error("Failed to connect via ethernet! Is the router's DHCP cache full?")
        print(" Connected.")

        m = re.search(r"WARP2 (?:CHARGER|Charger) V(\d+).(\d+).(\d+)", event_log)
        if not m:
            fatal_error("Failed to find version number in event log!" + event_log)

        version = [int(x) for x in m.groups()]
        latest_version = [int(x) for x in re.search(r"warp2_charger_firmware_(\d+)_(\d+)_(\d+).bin", firmware_path).groups()]

        if version > latest_version:
            fatal_error("Flashed firmware {}.{}.{} is not released yet! Latest released is {}.{}.{}".format(*version, *latest_version))
        elif version < latest_version:
            print("Flashed firmware {}.{}.{} is outdated! Flashing {}.{}.{}...".format(*version, *latest_version))

            with open(firmware_path, "rb") as f:
                fw = f.read()

            opener = urllib.request.build_opener(ContentTypeRemover())
            for i in range(5):
                try:
                    req = urllib.request.Request("http://{}/flash_firmware".format(ssid), fw)
                    print(opener.open(req).read().decode())
                    break
                except urllib.error.HTTPError as e:
                    print("HTTP error", e)
                    if e.code == 423:
                        fatal_error("Wallbox blocked firmware update. Is the EVSE working correctly?")
                    else:
                        fatal_error(e.read().decode("utf-8"))
                except urllib.error.URLError as e:
                    print("URL error", e)
                    if i != 4:
                        print("Failed to flash firmware. Retrying...")
                        time.sleep(3)
                    else:
                        if isinstance(e.reason, ConnectionResetError):
                            fatal_error("Wallbox blocked firmware update. Is the EVSE working correctly?")
                        fatal_error("Can't flash firmware!")

            time.sleep(3)

            print("Triggering factory reset")
            print("Connecting via ethernet to {}".format(ssid), end="")
            for i in range(45):
                start = time.monotonic()
                try:
                    req = urllib.request.Request("http://{}/factory_reset".format(ssid),
                                 data=json.dumps({"do_i_know_what_i_am_doing":True}).encode("utf-8"),
                                 method='PUT',
                                 headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=1) as f:
                        f.read()
                        break
                except Exception as e:
                    pass
                t = max(0, 1 - (time.monotonic() - start))
                time.sleep(t)
                print(".", end="")
            else:
                fatal_error("Failed to connect via ethernet!")
            print(" Connected.")
            print("Factory reset triggered.. Waiting 10 seconds")
            time.sleep(10)
        else:
            print("Flashed firmware is up-to-date.")

        result["firmware"] = firmware_path.split("/")[-1]

        print("Connecting via ethernet to {}".format(ssid), end="")
        for i in range(45):
            start = time.monotonic()
            try:
                with urllib.request.urlopen("http://{}/hidden_proxy/enable".format(ssid), timeout=1) as f:
                    f.read()
                    break
            except:
                pass
            t = max(0, 1 - (time.monotonic() - start))
            time.sleep(t)
            print(".", end="")
        else:
            fatal_error("Failed to connect via ethernet!")
        print(" Connected.")

        ipcon = IPConnection()
        try:
            ipcon.connect(ssid, 4223)
        except Exception as e:
            fatal_error("Failed to connect to ESP proxy. Is the router's DHCP cache full?")

        run_bricklet_tests(ipcon, result, qr_variant, qr_power, ssid, stage3)

        print("Configuring tags      ")
        req = urllib.request.Request("http://{}/nfc/config_update".format(ssid),
                                 data=json.dumps({"require_tag_to_start":False,
                                                  "require_tag_to_stop":False,
                                                  "authorized_tags": [{
                                                    "tag_name": "Tag 1",
                                                    "tag_type": seen_tags[0].tag_type,
                                                    "tag_id": seen_tags[0].tag_id
                                                    }, {
                                                    "tag_name": "Tag 2",
                                                    "tag_type": seen_tags[1].tag_type,
                                                    "tag_id": seen_tags[1].tag_id
                                                    }, {
                                                    "tag_name": "Tag 3",
                                                    "tag_type": seen_tags[2].tag_type,
                                                    "tag_id": seen_tags[2].tag_id
                                                    }
                                                  ]}).encode("utf-8"),
                                 method='PUT',
                                 headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=1) as f:
                f.read()
        except Exception as e:
            fatal_error("Failed to configure NFC tags!")
        result["nfc_tags_configured"] = True
    else:
        if docket_supply_cable_extension != 0 or docket_has_cee:
            stage3.power_on('CEE')
        else:
            stage3.power_on({"B": "Basic", "S": "Smart", "P": "Pro"}[qr_variant])

        result["uid"] = None

        ipcon = IPConnection()
        ipcon.connect("localhost", 4223)

        run_bricklet_tests(ipcon, result, qr_variant, qr_power, None, stage3)
        print("Flashing EVSE")
        run(["python3", "comcu_flasher.py", result["evse_uid"], evse_path])
        result["evse_firmware"] = evse_path.split("/")[-1]

    print("Checking if EVSE was tested...")
    if not exists_evse_test_report(result["evse_uid"]):
        print("No test report found for EVSE {}. Checking for new test reports...".format(result["evse_uid"]))
        with ChangedDirectory(os.path.join("..", "..", "wallbox")):
            run(["git", "pull"])
        if not exists_evse_test_report(result["evse_uid"]):
            fatal_error("Still no test report found for EVSE {}.".format(result["evse_uid"]))

    print("EVSE test report found")
    result["evse_test_report_found"] = True

    if qr_variant == "B":
        ssid = "warp2-" + result["evse_uid"]

    browser = None
    try:
        if qr_variant != "B":
            browser = webdriver.Firefox()
            browser.get("http://{}".format(ssid))

            element = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Ladecontroller"))
            )
            element.click()

        print("Performing the electrical tests")
        stage3.test_wallbox()
    finally:
        if browser is not None:
            browser.quit()

    print("Electrical tests passed")
    result["electrical_tests_passed"] = True
    result["end"] = now()

    with open("{}_{}_report_stage_2.json".format(ssid, now().replace(":", "-")), "w") as f:
        json.dump(result, f, indent=4)

    print('Done!')

if __name__ == "__main__":
    try:
        led_wrap()
    except FatalError:
        sys.exit(1)
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
