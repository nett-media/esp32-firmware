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

import bsCustomFileInput from "bs-custom-file-input";

interface Version {
    firmware: string,
    spiffs: string
}

let last_version: string = null;

function update_version(version: Version) {
    if (last_version == null) {
        last_version = version.firmware;
    } else if (last_version != version.firmware) {
        window.location.reload();
    }

    $('#current_firmware').val(version.firmware);
    $('#current_spiffs').val(version.spiffs);
}

function check_upload(type: string) {
    let file_select = <HTMLInputElement>$(`#${type}_file_select`)[0];

    $.ajax({
        timeout: 0,
        url: `/check_${type}`,
        type: 'POST',
        data: file_select.files[0].slice(0xd000 - 0x1000, 0xd000),
        contentType: false,
        processData: false,
        success: () => {
            upload(type);
        },
        error: (xhr, status, error) => {
            if (xhr.status == 423)
                util.add_alert("firmware_update_failed", "alert-danger", __("firmware_update.script.flash_fail"), __("firmware_update.script.vehicle_connected"));
            else {
                try {
                    let e = JSON.parse(xhr.responseText)
                    let error_message = __/* hide this from the translation checker */(e["error"])
                    if (e["error"] == "firmware_update.script.downgrade") {
                        error_message = error_message.replace("%fw%", e["fw"]).replace("%installed%", e["installed"]);
                        $('#downgrade_text').text(error_message);
                        $('#downgrade_modal').modal('show');
                    } else {
                        util.add_alert("firmware_update_failed","alert-danger", __("firmware_update.script.flash_fail"), error_message);
                    }
                } catch {
                    util.add_alert("firmware_update_failed","alert-danger", __("firmware_update.script.flash_fail"), error + ": " + xhr.responseText);
                }
            }
        }
    });
}

function upload(type: string) {
    util.pauseWebSockets();

    let file_select = <HTMLInputElement>$(`#${type}_file_select`)[0];
    let progress = $(`#${type}-progress`);
    let select = $(`#${type}_select`);
    let progress_bar = $(`#${type}-progress-bar`);

    progress.prop("hidden", false);
    select.prop("hidden", true);

    $.ajax({
        timeout: 0,
        url: `/flash_${type}`,
        type: 'POST',
        data: file_select.files[0],
        contentType: false,
        processData: false,
        xhr: function () {
            let xhr = new window.XMLHttpRequest();
            xhr.upload.addEventListener('progress', function (evt) {
                if (evt.lengthComputable) {
                    let per = evt.loaded / evt.total;
                    progress_bar.prop('style', "width: " + (per * 100) + "%");
                    progress_bar.prop('aria-valuenow', (per * 100));
                }
            }, false);
            return xhr;
        },
        success: () => {
            progress.prop("hidden", true);
            select.prop("hidden", false);
            util.postReboot(__("firmware_update.script.flash_success"), __("util.reboot_text"));
        },
        error: (xhr, status, error) => {
            progress.prop("hidden", true);
            select.prop("hidden", false);
            if (xhr.status == 423)
                util.add_alert("firmware_update_failed", "alert-danger", __("firmware_update.script.flash_fail"), __("firmware_update.script.vehicle_connected"));
            else {
                let txt = xhr.responseText.startsWith("firmware_update.") ? __/* hide this from the translation checker */(xhr.responseText) : error + ": " + xhr.responseText;
                util.add_alert("firmware_update_failed","alert-danger", __("firmware_update.script.flash_fail"), txt);
            }
            util.resumeWebSockets();
        }
    });
}

function factory_reset_modal() {
    $('#factory_reset_modal').modal('show');
}

function factory_reset() {
    $.ajax({
        url: `/factory_reset`,
        type: 'PUT',
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"do_i_know_what_i_am_doing": true}),
        success: () => {
            $('#factory_reset_modal').modal('hide');
            util.postReboot(__("firmware_update.script.factory_reset_init"), __("util.reboot_text"));
        },
        error: (xhr, status, error) => {
            $('#factory_reset_modal').modal('hide');
            util.add_alert("factory_reset_failed", "alert-danger", __("firmware_update.script.factory_reset_error"), error + ": " + xhr.responseText);
        }
    });
}

export function init() {
    // Firmware upload
    $('#upload_firmware_form').on("submit", function (e) {
        e.preventDefault();
        check_upload("firmware");
    });

    $('#downgrade_confirm').on("click", () => {
        $('#downgrade_modal').modal('hide');
        upload("firmware");
    });

    $('#firmware_file_select').on("change", () => $("#update_firmware_button").prop("disabled", false));

    $('#spiffs_factory_reset').on("click", factory_reset_modal);
    $('#factory_reset_confirm').on("click", factory_reset);
    $('#reboot').on("click", util.reboot);

    bsCustomFileInput.init();
}

export function addEventListeners(source: EventSource) {
    source.addEventListener('version', function (e: util.SSE) {
        update_version(<Version>(JSON.parse(e.data)));
    }, false);
}

export function updateLockState(module_init: any) {
    $('#sidebar-flash').prop('hidden', !module_init.firmware_update);
    $('#sidebar-system').prop('hidden',  $('#sidebar-system').prop('hidden') && !module_init.firmware_update);
}
