/* esp32-firmware
 * Copyright (C) 2021 Erik Fleckstein <erik@tinkerforge.com>
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

import feather = require("feather-icons");

declare function __(s: string): string;

interface Charger {
    name: string,
    last_update: number,
    uptime: number,
    supported_current: number,
    allowed_current: number,
    wants_to_charge: boolean,
    wants_to_charge_low_priority: boolean,
    is_charging: boolean,
    last_sent_config: number,
    allocated_current: number,
    state: number,
    error: number
}

interface ChargeManagerState {
    state: number,
    uptime: number,
    chargers: Charger[]
}

interface ChargerConfig {
    host: string,
    name: string
}

interface ChargeManagerConfig {
    enable_charge_manager: boolean,
    enable_watchdog: boolean,
    verbose: boolean,
    default_available_current: number,
    maximum_available_current: number,
    minimum_current: number,
    chargers: ChargerConfig[]
}

let charger_state_count = -1;

function update_charge_manager_state(state: ChargeManagerState) {
    if (state.chargers.length != charger_state_count) {
        let charger_content = "";
        let charger_status = "";
        for (let i = 0; i < state.chargers.length; i++) {
            if (i % 2 == 0) {
                if (i != 0) {
                    charger_status += '</div>';
                }
                charger_status += '<div class="card-deck mb-4">';
            }

            charger_status += `
            <div class="card">
                <h5 id="charge_manager_status_charger_${i}_name" class="card-header"></h5>
                <div id="charge_manager_status_charger_${i}_body" class="card-body">
                    <h5 id="charge_manager_status_charger_${i}_state" class="card-title"></h5>
                    <p id="charge_manager_status_charger_${i}_info" class="card-text"></p>
                </div>
                <div class="card-footer">
                    <small id="charge_manager_status_charger_${i}_details"></small>
                </div>
            </div>
            `
        }
        charger_status += '</div>';
        $('#charge_manager_content').html(charger_content);
        $('#charge_manager_status_chargers').html(charger_status);
        charger_state_count = state.chargers.length;
        $('#charge_manager_status_controlled_chargers').prop('hidden', charger_state_count == 0);
        $('#charge_manager_status_available_current_form').prop('hidden', charger_state_count == 0);
    }
    for (let i = 0; i < state.chargers.length; i++) {
        const s = state.chargers[i];

        $(`#charge_manager_status_charger_${i}_name`).text(s.name);
        if (s.state != 5) {
            if (state.state == 2) {
                $(`#charge_manager_status_charger_${i}_body`).addClass("bg-danger text-white bg-disabled");
                $(`#charge_manager_status_charger_${i}_state`).text(__("charge_manager.script.charge_state_blocked_by_other_box"));
                $(`#charge_manager_status_charger_${i}_info`).text(__("charge_manager.script.charge_state_blocked_by_other_box_details"));
            } else {
                $(`#charge_manager_status_charger_${i}_body`).removeClass("bg-danger text-white bg-disabled");
                $(`#charge_manager_status_charger_${i}_state`).text(__(`charge_manager.script.charge_state_${s.state}`));
                $(`#charge_manager_status_charger_${i}_info`).text(util.toLocaleFixed(s.allocated_current / 1000.0, 3) + " " + __("charge_manager.script.ampere_allocated"));
            }
        }
        else {
            if (s.error < 192)
                $(`#charge_manager_status_charger_${i}_state`).text(__("charge_manager.script.charge_error_type_management"));
            else
                $(`#charge_manager_status_charger_${i}_state`).text(__("charge_manager.script.charge_error_type_client"));

            $(`#charge_manager_status_charger_${i}_body`).addClass("bg-danger text-white bg-disabled");
            $(`#charge_manager_status_charger_${i}_info`).text(__(`charge_manager.script.charge_error_${s.error}`));
        }

        let last_update = Math.floor((state.uptime - s.last_update) / 1000);
        let status_text = util.toLocaleFixed(s.supported_current / 1000.0, 3) + " " + __("charge_manager.script.ampere_supported");

        if (last_update >= 10)
            status_text += "; " + __("charge_manager.script.last_update_prefix") + util.format_timespan(last_update) + (__("charge_manager.script.last_update_suffix"));
        $(`#charge_manager_status_charger_${i}_details`).text(status_text);
    }

    util.update_button_group("btn_group_charge_manager_state", state.state);
}

let charger_config_count = -1;

function set_available_current(current: number) {
    $('#charge_manager_status_available_current_save').prop("disabled", true);
    $.ajax({
        url: '/charge_manager/available_current_update',
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({"current": current}),
        success: () => {
            $('#charge_manager_status_available_current_save').html(feather.icons.check.toSvg());
        },
        error: (xhr, status, error) => {
            $('#charge_manager_status_available_current_save').prop("disabled", false);
            util.add_alert("charge_manager_set_available_current_failed", "alert-danger", __("charge_manager.script.set_available_current_failed"), error + ": " + xhr.responseText);
        }
    });
}

function update_available_current(current: number) {
    if($('#charge_manager_status_available_current_save').prop("disabled")) {
        util.setNumericInput("charge_manager_status_available_current", current / 1000, 3);
    }
}

function update_charge_manager_config(config: ChargeManagerConfig, force: boolean) {
    $('#charge_manager_status_available_current').prop("max", config.maximum_available_current / 1000.0);
    $("#charge_manager_status_available_current_maximum").on("click", () => set_available_current(config.default_available_current));
    $('#charge_manager_status_available_current_maximum').html(util.toLocaleFixed(config.default_available_current / 1000.0, 0) + " A");

    update_available_current(config.default_available_current);

    if (!force && !$('#charge_manager_save_button').prop("disabled"))
        return;

    $('#charge_manager_enable').prop("checked", config.enable_charge_manager);
    $('#charge_manager_enable_watchdog').prop("checked", config.enable_watchdog);
    $('#charge_manager_verbose').prop("checked", config.verbose);
    util.setNumericInput("charge_manager_default_available_current", config.default_available_current / 1000, 3);
    util.setNumericInput("charge_manager_maximum_available_current", config.maximum_available_current / 1000, 3);
    util.setNumericInput("charge_manager_minimum_current", config.minimum_current / 1000, 3);

    if (config.chargers.length != charger_config_count) {
        let charger_configs = "";
        for (let i = 0; i < config.chargers.length; i++) {
            charger_configs += `<div class="col mb-4">
                    <div class="card h-100">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <span class="h5" id="charge_manager_config_charger_${i}_name" style="margin-bottom: 0"></span>
                            <button type="button" class="btn btn-sm btn-outline-secondary"
                                id="charge_manager_content_${i}_remove">
                                <span data-feather="trash-2"></span>
                            </button>
                        </div>

                        <div class="card-body">
                            <div class="form-group">
                                <label for="charge_manager_config_charger_${i}_host">Host</label>
                                <input type="text" class="form-control" id="charge_manager_config_charger_${i}_host">
                            </div>
                        </div>
                    </div>
                </div>`;
        }
        charger_configs += `<div class="col mb-4">
        <div class="card h-100">
            <div class="card-header d-flex justify-content-between align-items-center">
                <span class="h5" style="margin-bottom: 0">${__("charge_manager.script.add_charger")}</span>
                <button type="button" class="btn btn-sm btn-outline-secondary" style="visibility: hidden;">
                        <span data-feather="trash-2"></span>
                </button>
            </div>
            <div class="card-body">
                <button id="charge_manager_add_charger" type="button" class="btn btn-light btn-lg btn-block" style="height: 100%;" data-toggle="modal" data-target="#charge_manager_add_charger_modal"><span data-feather="plus-circle"></span></button>
                <span id="charge_manager_add_charger_disabled" hidden>${__("charge_manager.script.add_charger_disabled")}</span>
            </div>
        </div>
    </div>`;
        $('#charge_manager_configs').html(charger_configs);
        charger_config_count = config.chargers.length;
        feather.replace();
        for (let i = 0; i < config.chargers.length; i++) {
            $(`#charge_manager_content_${i}_remove`).on("click", () => {
                $('#charge_manager_save_button').prop("disabled", false);
                update_charge_manager_config(collect_charge_manager_config(null, i), true);
            });
        }
    }

    $('#charge_manager_add_charger').prop("hidden", config.chargers.length >= 10);
    $('#charge_manager_add_charger_disabled').prop("hidden", config.chargers.length < 10);

    for (let i = 0; i < config.chargers.length; i++) {
        const s = config.chargers[i];
        $(`#charge_manager_config_charger_${i}_name`).html(s.name);
        $(`#charge_manager_config_charger_${i}_host`).val(s.host);
    }
}

function collect_charge_manager_config(new_charger: ChargerConfig = null, remove_charger: number = null) : ChargeManagerConfig {
    let chargers: ChargerConfig[] = [];
    for(let i = 0; i < charger_config_count; ++i) {
        if (remove_charger !== null && i == remove_charger)
            continue;
        let c: ChargerConfig = {
            host: $(`#charge_manager_config_charger_${i}_host`).val().toString(),
            name: $(`#charge_manager_config_charger_${i}_name`).html().toString(),
        }
        chargers.push(c);
    }
    if (new_charger != null)
        chargers.push(new_charger);

    return {
       enable_charge_manager: $('#charge_manager_enable').is(':checked'),
       enable_watchdog: $('#charge_manager_enable_watchdog').is(':checked'),
       verbose: $('#charge_manager_verbose').is(':checked'),
       default_available_current: Math.round(<number>$('#charge_manager_default_available_current').val() * 1000),
       maximum_available_current: Math.round(<number>$('#charge_manager_maximum_available_current').val() * 1000),
       minimum_current: Math.round(<number>$('#charge_manager_minimum_current').val() * 1000),
       chargers: chargers
    };
}

function save_charge_manager_config() {
    let payload = collect_charge_manager_config();

    $.ajax({
        url: '/charge_manager/config_update',
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: () => {
            $('#charge_manager_save_button').prop("disabled", true);
            $('#charge_manager_reboot').modal('show');
        },
        error: (xhr, status, error) => util.add_alert("charge_manager_config_update_failed", "alert-danger", __("charge_manager.script.save_failed"), error + ": " + xhr.responseText)
    });
}

function charge_manager_save_reboot() {
    $('#charge_manager_reboot').modal('hide');
    util.reboot();
}

export function init() {
    (<HTMLButtonElement>document.getElementById("charge_manager_reboot_button")).addEventListener("click", charge_manager_save_reboot);

    let form = <HTMLFormElement>$('#charge_manager_config_form')[0];
    form.addEventListener('input', function (event: Event) {
        $('#charge_manager_save_button').prop("disabled", false);
    }, false);

    form.addEventListener('submit', function (event: Event) {
        $('#charge_manager_default_available_current').prop("max", $('#charge_manager_maximum_available_current').val());

        form.classList.add('was-validated');
        event.preventDefault();
        event.stopPropagation();

        if (form.checkValidity() === false) {
            return;
        }

        save_charge_manager_config();
    }, false);

    $('#charge_manager_add_charger_form').on("submit", (event: Event) => {
        let form = <HTMLFormElement>$('#charge_manager_add_charger_form')[0];

        form.classList.add('was-validated');
        event.preventDefault();
        event.stopPropagation();

        if (form.checkValidity() === false) {
            return;
        }

        $('#charge_manager_add_charger_modal').modal('hide');
        $('#charge_manager_save_button').prop("disabled", false);

        let new_config = collect_charge_manager_config({
            host: $(`#charge_manager_config_charger_new_host`).val().toString(),
            name: $(`#charge_manager_config_charger_new_name`).val().toString(),
        }, null);

        update_charge_manager_config(new_config, true);
    });

    $("#charge_manager_status_available_current_minimum").on("click", () => set_available_current(0));

    let input = $('#charge_manager_status_available_current');
    let save_btn = $('#charge_manager_status_available_current_save');
    input.on("input", () => {
        save_btn.html(feather.icons.save.toSvg());
        save_btn.prop("disabled", false);
    });


    let form2 = <HTMLFormElement>$('#charge_manager_status_available_current_form')[0];

    form2.addEventListener('submit', function (event: Event) {
        event.preventDefault();
        event.stopPropagation();

        if (form.checkValidity() === false) {
            return;
        }

        set_available_current(Math.round(<number>input.val() * 1000));
    }, false);
}

export function addEventListeners(source: EventSource) {
    source.addEventListener('charge_manager/state', function (e: util.SSE) {
        update_charge_manager_state(<ChargeManagerState>(JSON.parse(e.data)));
    }, false);

    source.addEventListener('charge_manager/config', function (e: util.SSE) {
        update_charge_manager_config(<ChargeManagerConfig>(JSON.parse(e.data)), false);
    }, false);

    source.addEventListener('charge_manager/available_current', function (e: util.SSE) {
        update_available_current(JSON.parse(e.data)["current"]);
    }, false);
}

export function updateLockState(module_init: any) {
    $('#sidebar-charge_manager').prop('hidden', !module_init.charge_manager);
}
