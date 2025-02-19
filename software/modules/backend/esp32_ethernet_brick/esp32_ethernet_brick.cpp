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

#include "esp32_ethernet_brick.h"

#include <Arduino.h>

#include "tools.h"
#include "hal_arduino_esp32_ethernet_brick/hal_arduino_esp32_ethernet_brick.h"

#define GREEN_LED 2
#define BLUE_LED 15
#define BUTTON 0

TF_HAL hal;
extern uint32_t uid_numeric;
extern char uid[7];
extern char passphrase[20];
extern int8_t blue_led_pin;
extern int8_t green_led_pin;
extern int8_t button_pin;

ESP32EthernetBrick::ESP32EthernetBrick()
{

}

void ESP32EthernetBrick::setup()
{
    check(tf_hal_create(&hal), "hal create");
    tf_hal_set_timeout(&hal, 100000);

    read_efuses(&uid_numeric, uid, passphrase);

    pinMode(GREEN_LED, OUTPUT);
    pinMode(BLUE_LED, OUTPUT);
    pinMode(BUTTON, INPUT);

    green_led_pin = GREEN_LED;
    blue_led_pin = BLUE_LED;
    button_pin = BUTTON;

}

void ESP32EthernetBrick::register_urls()
{

}

void ledBlink(int8_t led_pin, int interval, int blinks_per_interval, int off_time_ms)
{
    int t_in_second = millis() % interval;
    if (off_time_ms != 0 && (interval - t_in_second <= off_time_ms)) {
        digitalWrite(led_pin, 1);
        return;
    }

    // We want blinks_per_interval blinks and blinks_per_interval pauses between them. The off_time counts as pause.
    int state_count = ((2 * blinks_per_interval) - (off_time_ms != 0 ? 1 : 0));
    int state_interval = (interval - off_time_ms) / state_count;
    bool led = (t_in_second / state_interval) % 2 != 0;

    digitalWrite(led_pin, led);
}

/*
The ESP Ethernet Brick can not trigger a factory reset itself,
as the ethernet phy clock disturbs any IO0 button reading.
*/
void ESP32EthernetBrick::loop()
{
    ledBlink(BLUE_LED, 2000, 1, 0);
}
