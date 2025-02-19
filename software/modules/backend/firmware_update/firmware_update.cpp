/* esp32-firmware
 * Copyright (C) 2020-2021 Erik Fleckstein <erik@tinkerforge.com>
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the
 * Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#include "firmware_update.h"

#include <Arduino.h>

#include <Update.h>
#include <LittleFS.h>

#include "event_log.h"
#include "task_scheduler.h"
#include "tools.h"
#include "build.h"

#include "./crc32.h"
#include "./recovery_page.h"

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

extern const char *DISPLAY_NAME;

extern EventLog logger;

extern WebServer server;
extern TaskScheduler task_scheduler;

extern bool firmware_update_allowed;
extern bool factory_reset_requested;
extern int8_t green_led_pin;

// Newer firmwares contain a firmware info page.
#define FW_INFO_OFFSET 0xd000 - 0x1000
#define FW_INFO_LENGTH 0x1000

TaskHandle_t xTaskBuffer;

void blinky(void *arg)
{
    for (;;) {
        digitalWrite(green_led_pin, true);
        delay(200);
        digitalWrite(green_led_pin, false);
        delay(200);
    }
}

static bool factory_reset_running = false;

void factory_reset()
{
    if (factory_reset_running)
        return;
    factory_reset_running = true;

    if (green_led_pin >= 0)
        xTaskCreate(blinky,
            "fctyrst_blink",
            2048,
            nullptr,
            tskIDLE_PRIORITY,
            &xTaskBuffer);

    LittleFS.end();
    LittleFS.format();
    ESP.restart();
}

FirmwareUpdate::FirmwareUpdate() {

}

void FirmwareUpdate::setup()
{
    initialized = true;
}

void FirmwareUpdate::reset_fw_info() {
    calculated_checksum = 0;
    info = fw_info_t{};
    info_offset = 0;
    checksum_offset = 0;
    update_aborted = false;
}

bool FirmwareUpdate::handle_fw_info_chunk(size_t chunk_index, uint8_t *data, size_t chunk_length)
{
    uint8_t *start = data;
    size_t length = chunk_length;

    if (chunk_index < FW_INFO_OFFSET) {
        size_t to_skip = FW_INFO_OFFSET - chunk_index;
        start += to_skip;
        length -= to_skip;
    }

    length = MIN(length, (FW_INFO_OFFSET + FW_INFO_LENGTH) - chunk_index - 4); // -4 to not calculate the CRC of itself

    if (info_offset < sizeof(info)) {
        size_t to_write = MIN(length, sizeof(info) - info_offset);
        memcpy(&info + info_offset, start, to_write);
        info_offset += to_write;
    }

    logger.printfln("chunk index %u data %p len %u", chunk_index, data, chunk_length);
    crc32_ieee_802_3_recalculate(start, length, &calculated_checksum);

    const size_t checksum_start = FW_INFO_OFFSET + FW_INFO_LENGTH - 4;

    if (chunk_index + chunk_length < checksum_start)
        return false;

    if (chunk_index < checksum_start) {
        size_t to_skip = checksum_start - chunk_index;
        start = data + to_skip;
        length = chunk_length - to_skip;
    }

    length = MIN(length, 4);

    if (checksum_offset < sizeof(checksum)) {
        size_t to_write = MIN(length, sizeof(checksum) - checksum_offset);
        memcpy(&checksum + checksum_offset, start, to_write);
        checksum_offset += to_write;
    }

    return checksum_offset == sizeof(checksum) && info.magic[0] == 0x12CE2171 && (info.magic[1] & 0x00FFFFFF) == 0x6E12F0;
}

String FirmwareUpdate::check_fw_info(bool fw_info_found, bool detect_downgrade, bool log) {
    if (!fw_info_found && BUILD_REQUIRE_FW_INFO) {
        if (log) {
            logger.printfln("Failed to update: Firmware update has no info page!");
        }
        return "{\"error\":\"firmware_update.script.no_info_page\"}";
    }
    if (fw_info_found) {
        if (checksum != calculated_checksum) {
            if (log) {
                logger.printfln("Failed to update: Firmware info page corrupted! Embedded checksum %x calculated checksum %x", checksum, calculated_checksum);
            }
            return "{\"error\":\"firmware_update.script.info_page_corrupted\"}";
        }

        if (strcmp(DISPLAY_NAME, info.firmware_name) != 0) {
            if (log) {
                logger.printfln("Failed to update: Firmware is for a %s but this is a %s!", info.firmware_name, DISPLAY_NAME);
            }
            return "{\"error\":\"firmware_update.script.wrong_firmware_type\"}";
        }

        if (detect_downgrade && compare_version(info.fw_version[0], info.fw_version[1], info.fw_version[2],
                                                BUILD_VERSION_MAJOR, BUILD_VERSION_MINOR, BUILD_VERSION_PATCH) < 0) {
            if (log) {
                logger.printfln("Failed to update: Firmware is a downgrade!");
            }
            char buf[128];
            snprintf(buf, sizeof(buf)/sizeof(buf[0]), "{\"error\":\"firmware_update.script.downgrade\", \"fw\":\"%u.%u.%u\", \"installed\":\"%u.%u.%u\"}",
                     info.fw_version[0], info.fw_version[1], info.fw_version[2],
                     BUILD_VERSION_MAJOR, BUILD_VERSION_MINOR, BUILD_VERSION_PATCH);
            return String(buf);
        }
    }
    return "";
}

bool FirmwareUpdate::handle_update_chunk(int command, WebServerRequest request, size_t chunk_index, uint8_t *data, size_t chunk_length, bool final, size_t complete_length) {
    // The firmware files are merged with the bootloader, partition table, firmware_info and slot configuration bins.
    // The bootloader starts at offset 0x1000, which is the first byte in the firmware file.
    // The first firmware slot (i.e. the one that is flashed over USB) starts at 0x10000.
    // So we have to skip the first 0x10000 - 0x1000 bytes, after them the actual firmware starts.
    // Don't skip anything if we flash the LittleFS.
    const size_t firmware_offset = command == U_FLASH ? 0x10000 - 0x1000 : 0;

    static bool fw_info_found = false;

    if (chunk_index == 0 && !Update.begin(complete_length - firmware_offset, command)) {
        logger.printfln("Failed to start update: %s", Update.errorString());
        request.send(400, "text/plain", Update.errorString());
        Update.abort();
        update_aborted = true;
        return true;
    }
    if (chunk_index == 0) {
        reset_fw_info();
        fw_info_found = false;
    }

    if (update_aborted)
        return true;

    if (chunk_index + chunk_length >= FW_INFO_OFFSET && chunk_index < FW_INFO_OFFSET + FW_INFO_LENGTH) {
        fw_info_found = handle_fw_info_chunk(chunk_index, data, chunk_length);
    }

    if (chunk_index + chunk_length >= FW_INFO_OFFSET + FW_INFO_LENGTH) {
        String error = this->check_fw_info(fw_info_found, false, true);
        if (error != "") {
            request.send(400, "text/plain", error.c_str());
            Update.abort();
            update_aborted = true;
            return true;
        }
    }

    if (chunk_index + chunk_length < firmware_offset) {
        return true;
    }

    uint8_t *start = data;
    size_t length = chunk_length;

    if (chunk_index < firmware_offset) {
        size_t to_skip = firmware_offset - chunk_index;
        start += to_skip;
        length -= to_skip;
    }

    auto written = Update.write(start, length);
    if (written != length) {
        logger.printfln("Failed to write update chunk with length %d; written %d, error: %s", length, written, Update.errorString());
        request.send(400, "text/plain", (String("Failed to write update: ") + Update.errorString()).c_str());
        this->firmware_update_running = false;
        Update.abort();
        return false;
    }

    if (final && !Update.end(true)) {
        logger.printfln("Failed to apply update: %s", Update.errorString());
        request.send(400, "text/plain", (String("Failed to apply update: ") + Update.errorString()).c_str());
        this->firmware_update_running = false;
        Update.abort();
        return false;
    }

    return true;
}

void FirmwareUpdate::register_urls()
{
    server.on("/recovery", HTTP_GET, [](WebServerRequest req) {
        req.addResponseHeader("Content-Encoding", "gzip");
        req.addResponseHeader("ETag", BUILD_TIMESTAMP_HEX_STR);
        req.send(200, "text/html", recovery_page, recovery_page_len);
    });

    server.on("/check_firmware", HTTP_POST, [this](WebServerRequest request){
        request.send(200, "text/plain", "{\"error\":\"firmware_update.script.ok\"}");
    },[this](WebServerRequest request, String filename, size_t index, uint8_t *data, size_t len, bool final){
        if (index == 0) {
            this->reset_fw_info();
        }
        if (!firmware_update_allowed) {
            request.send(400, "text/plain", "{\"error\":\"firmware_update.script.vehicle_connected\"}");
            return false;
        }

        if (index > FW_INFO_LENGTH) {
            request.send(400, "text/plain", "Too long!");
            return false;
        }

        bool fw_info_found = handle_fw_info_chunk(index + FW_INFO_OFFSET, data, len);

        if (index + len >= FW_INFO_LENGTH) {
            String error = this->check_fw_info(fw_info_found, true, false);
            if (error != "") {
                request.send(400, "text/plain", error.c_str());
            }
        }
        return true;
    });

    server.on("/flash_firmware", HTTP_POST, [this](WebServerRequest request){
        if (update_aborted)
            return;

        this->firmware_update_running = false;
        if (!firmware_update_allowed) {
            request.send(423, "text/plain", "vehicle connected");
            return;
        }

        if(!Update.hasError()) {
            task_scheduler.scheduleOnce("flash_firmware_reboot", [](){ESP.restart();}, 1000);
        }

        request.send(Update.hasError() ? 400: 200, "text/plain", Update.hasError() ? Update.errorString() : "Update OK");
    },[this](WebServerRequest request, String filename, size_t index, uint8_t *data, size_t len, bool final){
        if (!firmware_update_allowed) {
            request.send(423, "text/plain", "vehicle connected");
            this->firmware_update_running = false;
            return false;
        }
        this->firmware_update_running = true;
        return handle_update_chunk(U_FLASH, request, index, data, len, final, request.contentLength());
    });

    server.on("/flash_spiffs", HTTP_POST, [this](WebServerRequest request){
        if(!Update.hasError()) {
            task_scheduler.scheduleOnce("flash_spiffs_reboot", [](){ESP.restart();}, 1000);
        }

        request.send(Update.hasError() ? 400: 200, "text/plain", Update.hasError() ? Update.errorString() : "Update OK");
    },[this](WebServerRequest request, String filename, size_t index, uint8_t *data, size_t len, bool final){
        return handle_update_chunk(U_SPIFFS, request, index, data, len, final, request.contentLength());
    });

    server.on("/factory_reset", HTTP_PUT, [this](WebServerRequest request) {
        char *payload = request.receive();
        StaticJsonDocument<16> doc;

        DeserializationError error = deserializeJson(doc, payload, request.contentLength());

        if (error) {
            logger.printfln("Failed to parse command payload: %s", error.c_str());
            request.send(400);
            free(payload);
            return;
        }

        if (!doc["do_i_know_what_i_am_doing"].is<bool>()) {
            request.send(400, "text/html", "you don't seem to know what you are doing");
            free(payload);
            return;
        }

        if (doc["do_i_know_what_i_am_doing"].as<bool>()) {
            task_scheduler.scheduleOnce("factory_reset", [](){
                logger.printfln("Factory reset requested");
                factory_reset();
            }, 3000);
            request.send(200, "text/html", "Factory reset initiated");
        } else {
            request.send(400, "text/html", "Factory reset NOT initiated");
        }

        free(payload);
    });
}

void FirmwareUpdate::loop()
{
    if (factory_reset_requested)
        factory_reset();
}
