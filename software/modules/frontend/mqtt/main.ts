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

import $ from "jquery";

import * as util from "../util";

declare function __(s: string): string;

interface MqttConfig {
    enable_mqtt: boolean,
    broker_host: string,
    broker_port: number,
    broker_username: string,
    broker_password: string,
    global_topic_prefix: string
    client_name: string
}

interface MqttState {
    connection_state: number
    last_error: number
}

function update_mqtt_config(config: MqttConfig) {
    // Remove the was-validated class to fix a visual bug
    // where saving the config triggers an update
    // that fills the elements, but clears the passphrase field.
    // An empty passphrase is invalid, so the input
    // field is marked as non-validated, confusing the user.
    let form = <HTMLFormElement>$('#mqtt_config_form')[0];
    form.classList.remove('was-validated');

    $('#mqtt_enable').prop("checked", config.enable_mqtt);
    $('#mqtt_broker_host').val(config.broker_host);
    $('#mqtt_broker_port').val(config.broker_port);
    $('#mqtt_broker_username').val(config.broker_username);
    // omit password
    $('#mqtt_topic_prefix').val(config.global_topic_prefix);
    $('#mqtt_client_name').val(config.client_name);
}

function save_mqtt_config() {
    let payload: MqttConfig = {
        enable_mqtt: $('#mqtt_enable').is(':checked'),
        broker_host: $('#mqtt_broker_host').val().toString(),
        broker_port: parseInt($('#mqtt_broker_port').val().toString(), 10),
        broker_username: $('#mqtt_broker_username').val().toString(),
        broker_password: util.passwordUpdate('#mqtt_broker_password'),
        global_topic_prefix: $('#mqtt_topic_prefix').val().toString(),
        client_name: $('#mqtt_client_name').val().toString(),
    };

    $.ajax({
        url: '/mqtt/config_update',
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: () => $('#mqtt_reboot').modal('show'),
        error: (xhr, status, error) => util.add_alert("mqtt_config_update_failed", "alert-danger", __("mqtt.script.save_failed"), error + ": " + xhr.responseText)
    });
}

function update_mqtt_state(state: MqttState) {
    util.update_button_group("btn_group_mqtt_state", state.connection_state);
    if(state.connection_state == 3) {
        $('#mqtt_status_error').html(" " + state.last_error);
    }
}

export function addEventListeners(source: EventSource) {
    source.addEventListener('mqtt/config', function (e: util.SSE) {
        update_mqtt_config(<MqttConfig>(JSON.parse(e.data)));
    }, false);

    source.addEventListener('mqtt/state', function (e: util.SSE) {
        update_mqtt_state(<MqttState>(JSON.parse(e.data)));
    }, false);
}

export function init() {
    let show_button = <HTMLButtonElement>document.getElementById("mqtt_show_password");
    show_button.addEventListener("change", util.toggle_password_fn("#mqtt_broker_password"));

    let clear_button = <HTMLButtonElement>document.getElementById("mqtt_clear_password");
    clear_button.addEventListener("change", util.clear_password_fn("#mqtt_broker_password"));

    let form = <HTMLFormElement>$('#mqtt_config_form')[0];
    form.addEventListener('submit', function (event: Event) {
        form.classList.add('was-validated');
        event.preventDefault();
        event.stopPropagation();

        if (form.checkValidity() === false) {
            return;
        }

        save_mqtt_config();
    }, false);

    (<HTMLButtonElement>document.getElementById("mqtt_reboot_button")).addEventListener("click", () => {
        $('#mqtt_reboot').modal('hide');
        util.reboot();
    });
}

export function updateLockState(module_init: any) {
    $('#sidebar-mqtt').prop('hidden', !module_init.mqtt);
}
