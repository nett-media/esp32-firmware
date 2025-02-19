# -*- coding: utf-8 -*-
#############################################################
# This file was automatically generated on 2021-11-04.      #
#                                                           #
# Python Bindings Version 2.1.29                            #
#                                                           #
# If you have a bugfix for this file and want to commit it, #
# please fix the bug in the generator. You can find a link  #
# to the generators git repository on tinkerforge.com       #
#############################################################

#### __DEVICE_IS_NOT_RELEASED__ ####

from collections import namedtuple

from tinkerforge.ip_connection import Device, IPConnection, Error, create_char, create_char_list, create_string, create_chunk_data

GetState = namedtuple('State', ['iec61851_state', 'vehicle_state', 'contactor_state', 'contactor_error', 'charge_release', 'allowed_charging_current', 'error_state', 'lock_state', 'time_since_state_change', 'uptime'])
GetHardwareConfiguration = namedtuple('HardwareConfiguration', ['jumper_configuration', 'has_lock_switch'])
GetLowLevelState = namedtuple('LowLevelState', ['led_state', 'cp_pwm_duty_cycle', 'adc_values', 'voltages', 'resistances', 'gpio', 'charging_time'])
GetMaxChargingCurrent = namedtuple('MaxChargingCurrent', ['max_current_configured', 'max_current_incoming_cable', 'max_current_outgoing_cable', 'max_current_managed'])
GetEnergyMeterValues = namedtuple('EnergyMeterValues', ['power', 'energy_relative', 'energy_absolute', 'phases_active', 'phases_connected'])
GetEnergyMeterDetailedValuesLowLevel = namedtuple('EnergyMeterDetailedValuesLowLevel', ['values_chunk_offset', 'values_chunk_data'])
GetEnergyMeterState = namedtuple('EnergyMeterState', ['available', 'error_count'])
GetGPIOConfiguration = namedtuple('GPIOConfiguration', ['shutdown_input_configuration', 'input_configuration', 'output_configuration'])
GetIndicatorLED = namedtuple('IndicatorLED', ['indication', 'duration'])
GetButtonState = namedtuple('ButtonState', ['button_press_time', 'button_release_time', 'button_pressed'])
GetAllData1 = namedtuple('AllData1', ['iec61851_state', 'vehicle_state', 'contactor_state', 'contactor_error', 'charge_release', 'allowed_charging_current', 'error_state', 'lock_state', 'time_since_state_change', 'uptime', 'jumper_configuration', 'has_lock_switch'])
GetAllData2 = namedtuple('AllData2', ['led_state', 'cp_pwm_duty_cycle', 'adc_values', 'voltages', 'resistances', 'gpio', 'charging_time', 'max_current_configured', 'max_current_incoming_cable', 'max_current_outgoing_cable', 'max_current_managed', 'autostart'])
GetAllData3 = namedtuple('AllData3', ['power', 'energy_relative', 'energy_absolute', 'phases_active', 'phases_connected', 'available', 'error_count', 'dc_fault_current_state', 'shutdown_input_configuration', 'input_configuration', 'output_configuration', 'managed', 'indication', 'duration', 'button_configuration', 'button_press_time', 'button_release_time', 'button_pressed', 'control_pilot'])
GetSPITFPErrorCount = namedtuple('SPITFPErrorCount', ['error_count_ack_checksum', 'error_count_message_checksum', 'error_count_frame', 'error_count_overflow'])
GetIdentity = namedtuple('Identity', ['uid', 'connected_uid', 'position', 'hardware_version', 'firmware_version', 'device_identifier'])

class BrickletEVSEV2(Device):
    """
    TBD
    """

    DEVICE_IDENTIFIER = 2167
    DEVICE_DISPLAY_NAME = 'EVSE Bricklet 2.0'
    DEVICE_URL_PART = 'evse_v2' # internal



    FUNCTION_GET_STATE = 1
    FUNCTION_GET_HARDWARE_CONFIGURATION = 2
    FUNCTION_GET_LOW_LEVEL_STATE = 3
    FUNCTION_SET_MAX_CHARGING_CURRENT = 4
    FUNCTION_GET_MAX_CHARGING_CURRENT = 5
    FUNCTION_START_CHARGING = 6
    FUNCTION_STOP_CHARGING = 7
    FUNCTION_SET_CHARGING_AUTOSTART = 8
    FUNCTION_GET_CHARGING_AUTOSTART = 9
    FUNCTION_GET_ENERGY_METER_VALUES = 10
    FUNCTION_GET_ENERGY_METER_DETAILED_VALUES_LOW_LEVEL = 11
    FUNCTION_GET_ENERGY_METER_STATE = 12
    FUNCTION_RESET_ENERGY_METER = 13
    FUNCTION_GET_DC_FAULT_CURRENT_STATE = 14
    FUNCTION_RESET_DC_FAULT_CURRENT = 15
    FUNCTION_SET_GPIO_CONFIGURATION = 16
    FUNCTION_GET_GPIO_CONFIGURATION = 17
    FUNCTION_GET_MANAGED = 18
    FUNCTION_SET_MANAGED = 19
    FUNCTION_SET_MANAGED_CURRENT = 20
    FUNCTION_GET_DATA_STORAGE = 21
    FUNCTION_SET_DATA_STORAGE = 22
    FUNCTION_GET_INDICATOR_LED = 23
    FUNCTION_SET_INDICATOR_LED = 24
    FUNCTION_SET_BUTTON_CONFIGURATION = 25
    FUNCTION_GET_BUTTON_CONFIGURATION = 26
    FUNCTION_GET_BUTTON_STATE = 27
    FUNCTION_SET_CONTROL_PILOT_CONFIGURATION = 28
    FUNCTION_GET_CONTROL_PILOT_CONFIGURATION = 29
    FUNCTION_GET_ALL_DATA_1 = 30
    FUNCTION_GET_ALL_DATA_2 = 31
    FUNCTION_GET_ALL_DATA_3 = 32
    FUNCTION_GET_SPITFP_ERROR_COUNT = 234
    FUNCTION_SET_BOOTLOADER_MODE = 235
    FUNCTION_GET_BOOTLOADER_MODE = 236
    FUNCTION_SET_WRITE_FIRMWARE_POINTER = 237
    FUNCTION_WRITE_FIRMWARE = 238
    FUNCTION_SET_STATUS_LED_CONFIG = 239
    FUNCTION_GET_STATUS_LED_CONFIG = 240
    FUNCTION_GET_CHIP_TEMPERATURE = 242
    FUNCTION_RESET = 243
    FUNCTION_WRITE_UID = 248
    FUNCTION_READ_UID = 249
    FUNCTION_GET_IDENTITY = 255

    IEC61851_STATE_A = 0
    IEC61851_STATE_B = 1
    IEC61851_STATE_C = 2
    IEC61851_STATE_D = 3
    IEC61851_STATE_EF = 4
    LED_STATE_OFF = 0
    LED_STATE_ON = 1
    LED_STATE_BLINKING = 2
    LED_STATE_FLICKER = 3
    LED_STATE_BREATHING = 4
    VEHICLE_STATE_NOT_CONNECTED = 0
    VEHICLE_STATE_CONNECTED = 1
    VEHICLE_STATE_CHARGING = 2
    VEHICLE_STATE_ERROR = 3
    CONTACTOR_STATE_AC1_NLIVE_AC2_NLIVE = 0
    CONTACTOR_STATE_AC1_LIVE_AC2_NLIVE = 1
    CONTACTOR_STATE_AC1_NLIVE_AC2_LIVE = 2
    CONTACTOR_STATE_AC1_LIVE_AC2_LIVE = 3
    LOCK_STATE_INIT = 0
    LOCK_STATE_OPEN = 1
    LOCK_STATE_CLOSING = 2
    LOCK_STATE_CLOSE = 3
    LOCK_STATE_OPENING = 4
    LOCK_STATE_ERROR = 5
    ERROR_STATE_OK = 0
    ERROR_STATE_SWITCH = 2
    ERROR_STATE_DC_FAULT = 3
    ERROR_STATE_CONTACTOR = 4
    ERROR_STATE_COMMUNICATION = 5
    JUMPER_CONFIGURATION_6A = 0
    JUMPER_CONFIGURATION_10A = 1
    JUMPER_CONFIGURATION_13A = 2
    JUMPER_CONFIGURATION_16A = 3
    JUMPER_CONFIGURATION_20A = 4
    JUMPER_CONFIGURATION_25A = 5
    JUMPER_CONFIGURATION_32A = 6
    JUMPER_CONFIGURATION_SOFTWARE = 7
    JUMPER_CONFIGURATION_UNCONFIGURED = 8
    CHARGE_RELEASE_AUTOMATIC = 0
    CHARGE_RELEASE_MANUAL = 1
    CHARGE_RELEASE_DEACTIVATED = 2
    CHARGE_RELEASE_MANAGED = 3
    DC_FAULT_CURRENT_STATE_NORMAL_CONDITION = 0
    DC_FAULT_CURRENT_STATE_6_MA_ERROR = 1
    DC_FAULT_CURRENT_STATE_SYSTEM_ERROR = 2
    DC_FAULT_CURRENT_STATE_UNKNOWN_ERROR = 3
    DC_FAULT_CURRENT_STATE_CALIBRATION_ERROR = 4
    SHUTDOWN_INPUT_IGNORED = 0
    SHUTDOWN_INPUT_SHUTDOWN_ON_OPEN = 1
    SHUTDOWN_INPUT_SHUTDOWN_ON_CLOSE = 2
    OUTPUT_LOW = 0
    OUTPUT_HIGH = 1
    BUTTON_CONFIGURATION_DEACTIVATED = 0
    BUTTON_CONFIGURATION_START_CHARGING = 1
    BUTTON_CONFIGURATION_STOP_CHARGING = 2
    BUTTON_CONFIGURATION_START_AND_STOP_CHARGING = 3
    CONTROL_PILOT_DISCONNECTED = 0
    CONTROL_PILOT_CONNECTED = 1
    CONTROL_PILOT_AUTOMATIC = 2
    BOOTLOADER_MODE_BOOTLOADER = 0
    BOOTLOADER_MODE_FIRMWARE = 1
    BOOTLOADER_MODE_BOOTLOADER_WAIT_FOR_REBOOT = 2
    BOOTLOADER_MODE_FIRMWARE_WAIT_FOR_REBOOT = 3
    BOOTLOADER_MODE_FIRMWARE_WAIT_FOR_ERASE_AND_REBOOT = 4
    BOOTLOADER_STATUS_OK = 0
    BOOTLOADER_STATUS_INVALID_MODE = 1
    BOOTLOADER_STATUS_NO_CHANGE = 2
    BOOTLOADER_STATUS_ENTRY_FUNCTION_NOT_PRESENT = 3
    BOOTLOADER_STATUS_DEVICE_IDENTIFIER_INCORRECT = 4
    BOOTLOADER_STATUS_CRC_MISMATCH = 5
    STATUS_LED_CONFIG_OFF = 0
    STATUS_LED_CONFIG_ON = 1
    STATUS_LED_CONFIG_SHOW_HEARTBEAT = 2
    STATUS_LED_CONFIG_SHOW_STATUS = 3

    def __init__(self, uid, ipcon):
        """
        Creates an object with the unique device ID *uid* and adds it to
        the IP Connection *ipcon*.
        """
        Device.__init__(self, uid, ipcon, BrickletEVSEV2.DEVICE_IDENTIFIER, BrickletEVSEV2.DEVICE_DISPLAY_NAME)

        self.api_version = (2, 0, 0)

        self.response_expected[BrickletEVSEV2.FUNCTION_GET_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_HARDWARE_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_LOW_LEVEL_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_MAX_CHARGING_CURRENT] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_MAX_CHARGING_CURRENT] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_START_CHARGING] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_STOP_CHARGING] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_CHARGING_AUTOSTART] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_CHARGING_AUTOSTART] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_VALUES] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_DETAILED_VALUES_LOW_LEVEL] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_RESET_ENERGY_METER] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_DC_FAULT_CURRENT_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_RESET_DC_FAULT_CURRENT] = BrickletEVSEV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_GPIO_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_GPIO_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_MANAGED] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_MANAGED] = BrickletEVSEV2.RESPONSE_EXPECTED_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_MANAGED_CURRENT] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_DATA_STORAGE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_DATA_STORAGE] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_INDICATOR_LED] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_INDICATOR_LED] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_BUTTON_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_BUTTON_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_BUTTON_STATE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_CONTROL_PILOT_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_CONTROL_PILOT_CONFIGURATION] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_ALL_DATA_1] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_ALL_DATA_2] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_ALL_DATA_3] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_SPITFP_ERROR_COUNT] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_BOOTLOADER_MODE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_BOOTLOADER_MODE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_WRITE_FIRMWARE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_SET_STATUS_LED_CONFIG] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_STATUS_LED_CONFIG] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_CHIP_TEMPERATURE] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_RESET] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_WRITE_UID] = BrickletEVSEV2.RESPONSE_EXPECTED_FALSE
        self.response_expected[BrickletEVSEV2.FUNCTION_READ_UID] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE
        self.response_expected[BrickletEVSEV2.FUNCTION_GET_IDENTITY] = BrickletEVSEV2.RESPONSE_EXPECTED_ALWAYS_TRUE


        ipcon.add_device(self)

    def get_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetState(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_STATE, (), '', 25, 'B B B B B H B B I I'))

    def get_hardware_configuration(self):
        """
        TODO
        """
        self.check_validity()

        return GetHardwareConfiguration(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_HARDWARE_CONFIGURATION, (), '', 10, 'B !'))

    def get_low_level_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetLowLevelState(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_LOW_LEVEL_STATE, (), '', 54, 'B H 7H 7h 2I 24! I'))

    def set_max_charging_current(self, max_current):
        """
        TODO
        """
        self.check_validity()

        max_current = int(max_current)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_MAX_CHARGING_CURRENT, (max_current,), 'H', 0, '')

    def get_max_charging_current(self):
        """
        * Max Current Configured -> set with :func:`Set Max Charging Current`
        * Max Current Incoming Cable -> set with jumper on EVSE
        * Max Current Outgoing Cable -> set with resistor between PP/PE (if fixed cable is used)

        TODO
        """
        self.check_validity()

        return GetMaxChargingCurrent(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_MAX_CHARGING_CURRENT, (), '', 16, 'H H H H'))

    def start_charging(self):
        """
        TODO
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_START_CHARGING, (), '', 0, '')

    def stop_charging(self):
        """
        TODO
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_STOP_CHARGING, (), '', 0, '')

    def set_charging_autostart(self, autostart):
        """
        TODO
        """
        self.check_validity()

        autostart = bool(autostart)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_CHARGING_AUTOSTART, (autostart,), '!', 0, '')

    def get_charging_autostart(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_CHARGING_AUTOSTART, (), '', 9, '!')

    def get_energy_meter_values(self):
        """
        TODO
        """
        self.check_validity()

        return GetEnergyMeterValues(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_VALUES, (), '', 22, 'f f f 3! 3!'))

    def get_energy_meter_detailed_values_low_level(self):
        """
        TBD
        """
        self.check_validity()

        return GetEnergyMeterDetailedValuesLowLevel(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_DETAILED_VALUES_LOW_LEVEL, (), '', 70, 'H 15f'))

    def get_energy_meter_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetEnergyMeterState(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_ENERGY_METER_STATE, (), '', 33, '! 6I'))

    def reset_energy_meter(self):
        """
        TODO
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_RESET_ENERGY_METER, (), '', 0, '')

    def get_dc_fault_current_state(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_DC_FAULT_CURRENT_STATE, (), '', 9, 'B')

    def reset_dc_fault_current(self, password):
        """
        TODO
        """
        self.check_validity()

        password = int(password)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_RESET_DC_FAULT_CURRENT, (password,), 'I', 0, '')

    def set_gpio_configuration(self, shutdown_input_configuration, input_configuration, output_configuration):
        """
        TODO
        """
        self.check_validity()

        shutdown_input_configuration = int(shutdown_input_configuration)
        input_configuration = int(input_configuration)
        output_configuration = int(output_configuration)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_GPIO_CONFIGURATION, (shutdown_input_configuration, input_configuration, output_configuration), 'B B B', 0, '')

    def get_gpio_configuration(self):
        """
        TODO
        """
        self.check_validity()

        return GetGPIOConfiguration(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_GPIO_CONFIGURATION, (), '', 11, 'B B B'))

    def get_managed(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_MANAGED, (), '', 9, '!')

    def set_managed(self, managed, password):
        """
        TODO
        """
        self.check_validity()

        managed = bool(managed)
        password = int(password)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_MANAGED, (managed, password), '! I', 0, '')

    def set_managed_current(self, current):
        """
        TODO
        """
        self.check_validity()

        current = int(current)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_MANAGED_CURRENT, (current,), 'H', 0, '')

    def get_data_storage(self, page):
        """
        TODO
        """
        self.check_validity()

        page = int(page)

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_DATA_STORAGE, (page,), 'B', 71, '63B')

    def set_data_storage(self, page, data):
        """
        TODO
        """
        self.check_validity()

        page = int(page)
        data = list(map(int, data))

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_DATA_STORAGE, (page, data), 'B 63B', 0, '')

    def get_indicator_led(self):
        """
        TODO
        """
        self.check_validity()

        return GetIndicatorLED(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_INDICATOR_LED, (), '', 12, 'h H'))

    def set_indicator_led(self, indication, duration):
        """
        TODO
        """
        self.check_validity()

        indication = int(indication)
        duration = int(duration)

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_INDICATOR_LED, (indication, duration), 'h H', 9, 'B')

    def set_button_configuration(self, button_configuration):
        """
        TODO
        """
        self.check_validity()

        button_configuration = int(button_configuration)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_BUTTON_CONFIGURATION, (button_configuration,), 'B', 0, '')

    def get_button_configuration(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_BUTTON_CONFIGURATION, (), '', 9, 'B')

    def get_button_state(self):
        """
        TODO
        """
        self.check_validity()

        return GetButtonState(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_BUTTON_STATE, (), '', 17, 'I I !'))

    def set_control_pilot_configuration(self, control_pilot):
        """
        TODO
        """
        self.check_validity()

        control_pilot = int(control_pilot)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_CONTROL_PILOT_CONFIGURATION, (control_pilot,), 'B', 0, '')

    def get_control_pilot_configuration(self):
        """
        TODO
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_CONTROL_PILOT_CONFIGURATION, (), '', 9, 'B')

    def get_all_data_1(self):
        """
        TODO
        """
        self.check_validity()

        return GetAllData1(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_ALL_DATA_1, (), '', 27, 'B B B B B H B B I I B !'))

    def get_all_data_2(self):
        """
        TODO
        """
        self.check_validity()

        return GetAllData2(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_ALL_DATA_2, (), '', 63, 'B H 7H 7h 2I 24! I H H H H !'))

    def get_all_data_3(self):
        """
        TODO
        """
        self.check_validity()

        return GetAllData3(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_ALL_DATA_3, (), '', 67, 'f f f 3! 3! ! 6I B B B B ! h H B I I ! B'))

    def get_spitfp_error_count(self):
        """
        Returns the error count for the communication between Brick and Bricklet.

        The errors are divided into

        * ACK checksum errors,
        * message checksum errors,
        * framing errors and
        * overflow errors.

        The errors counts are for errors that occur on the Bricklet side. All
        Bricks have a similar function that returns the errors on the Brick side.
        """
        self.check_validity()

        return GetSPITFPErrorCount(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_SPITFP_ERROR_COUNT, (), '', 24, 'I I I I'))

    def set_bootloader_mode(self, mode):
        """
        Sets the bootloader mode and returns the status after the requested
        mode change was instigated.

        You can change from bootloader mode to firmware mode and vice versa. A change
        from bootloader mode to firmware mode will only take place if the entry function,
        device identifier and CRC are present and correct.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        mode = int(mode)

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_BOOTLOADER_MODE, (mode,), 'B', 9, 'B')

    def get_bootloader_mode(self):
        """
        Returns the current bootloader mode, see :func:`Set Bootloader Mode`.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_BOOTLOADER_MODE, (), '', 9, 'B')

    def set_write_firmware_pointer(self, pointer):
        """
        Sets the firmware pointer for :func:`Write Firmware`. The pointer has
        to be increased by chunks of size 64. The data is written to flash
        every 4 chunks (which equals to one page of size 256).

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        pointer = int(pointer)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_WRITE_FIRMWARE_POINTER, (pointer,), 'I', 0, '')

    def write_firmware(self, data):
        """
        Writes 64 Bytes of firmware at the position as written by
        :func:`Set Write Firmware Pointer` before. The firmware is written
        to flash every 4 chunks.

        You can only write firmware in bootloader mode.

        This function is used by Brick Viewer during flashing. It should not be
        necessary to call it in a normal user program.
        """
        self.check_validity()

        data = list(map(int, data))

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_WRITE_FIRMWARE, (data,), '64B', 9, 'B')

    def set_status_led_config(self, config):
        """
        Sets the status LED configuration. By default the LED shows
        communication traffic between Brick and Bricklet, it flickers once
        for every 10 received data packets.

        You can also turn the LED permanently on/off or show a heartbeat.

        If the Bricklet is in bootloader mode, the LED is will show heartbeat by default.
        """
        self.check_validity()

        config = int(config)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_SET_STATUS_LED_CONFIG, (config,), 'B', 0, '')

    def get_status_led_config(self):
        """
        Returns the configuration as set by :func:`Set Status LED Config`
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_STATUS_LED_CONFIG, (), '', 9, 'B')

    def get_chip_temperature(self):
        """
        Returns the temperature as measured inside the microcontroller. The
        value returned is not the ambient temperature!

        The temperature is only proportional to the real temperature and it has bad
        accuracy. Practically it is only useful as an indicator for
        temperature changes.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_CHIP_TEMPERATURE, (), '', 10, 'h')

    def reset(self):
        """
        Calling this function will reset the Bricklet. All configurations
        will be lost.

        After a reset you have to create new device objects,
        calling functions on the existing ones will result in
        undefined behavior!
        """
        self.check_validity()

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_RESET, (), '', 0, '')

    def write_uid(self, uid):
        """
        Writes a new UID into flash. If you want to set a new UID
        you have to decode the Base58 encoded UID string into an
        integer first.

        We recommend that you use Brick Viewer to change the UID.
        """
        self.check_validity()

        uid = int(uid)

        self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_WRITE_UID, (uid,), 'I', 0, '')

    def read_uid(self):
        """
        Returns the current UID as an integer. Encode as
        Base58 to get the usual string version.
        """
        self.check_validity()

        return self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_READ_UID, (), '', 12, 'I')

    def get_identity(self):
        """
        Returns the UID, the UID where the Bricklet is connected to,
        the position, the hardware and firmware version as well as the
        device identifier.

        The position can be 'a', 'b', 'c', 'd', 'e', 'f', 'g' or 'h' (Bricklet Port).
        A Bricklet connected to an :ref:`Isolator Bricklet <isolator_bricklet>` is always at
        position 'z'.

        The device identifier numbers can be found :ref:`here <device_identifier>`.
        |device_identifier_constant|
        """
        return GetIdentity(*self.ipcon.send_request(self, BrickletEVSEV2.FUNCTION_GET_IDENTITY, (), '', 33, '8s 8s c 3B 3B H'))

    def get_energy_meter_detailed_values(self):
        """
        TBD
        """
        values_length = 85

        with self.stream_lock:
            ret = self.get_energy_meter_detailed_values_low_level()

            if ret.values_chunk_offset == (1 << 16) - 1: # maximum chunk offset -> stream has no data
                values_length = 0
                values_out_of_sync = False
                values_data = ()
            else:
                values_out_of_sync = ret.values_chunk_offset != 0
                values_data = ret.values_chunk_data

            while not values_out_of_sync and len(values_data) < values_length:
                ret = self.get_energy_meter_detailed_values_low_level()
                values_out_of_sync = ret.values_chunk_offset != len(values_data)
                values_data += ret.values_chunk_data

            if values_out_of_sync: # discard remaining stream to bring it back in-sync
                while ret.values_chunk_offset + 15 < values_length:
                    ret = self.get_energy_meter_detailed_values_low_level()

                raise Error(Error.STREAM_OUT_OF_SYNC, 'Values stream is out-of-sync')

        return values_data[:values_length]

EVSEV2 = BrickletEVSEV2 # for backward compatibility
