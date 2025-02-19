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

#include "mqtt.h"

#include <Arduino.h>

#include "task_scheduler.h"
#include "tools.h"
#include "api.h"
#include "event_log.h"
#include "build.h"

extern EventLog logger;

extern TaskScheduler task_scheduler;
extern char uid[7];
extern API api;

#define MQTT_RECV_BUFFER_SIZE 4096
#define MQTT_RECV_BUFFER_HEADROOM (MQTT_RECV_BUFFER_SIZE / 4)

Mqtt::Mqtt()
{
    // The real UID will be patched in later
    mqtt_config = Config::Object({
        {"enable_mqtt", Config::Bool(false)},
        {"broker_host", Config::Str("", 128)},
        {"broker_port", Config::Uint16(1883)},
        {"broker_username", Config::Str("", 64)},
        {"broker_password", Config::Str("", 64)},
        {"global_topic_prefix", Config::Str(String(BUILD_HOST_PREFIX) + String("/") + String("ABC"), 64)},
        {"client_name", Config::Str(String(BUILD_HOST_PREFIX) + String("-") + String("ABC"), 64, [](Config::ConfString &s) -> String {
            if (s.value.length() >= 1)
                return "";
            return "Client ID must be at least one character long";
            })
        }
    });

    mqtt_state = Config::Object({
        {"connection_state", Config::Int(0)},
        {"last_error", Config::Int(0)}
    });
}

void Mqtt::subscribe(String topic_suffix, uint32_t max_payload_length, std::function<void(char *, size_t)> callback, bool forbid_retained)
{
    String prefix = mqtt_config_in_use.get("global_topic_prefix")->asString();
    String topic = prefix + "/" + topic_suffix;
    this->commands.push_back({topic, max_payload_length, callback, forbid_retained});

    esp_mqtt_client_unsubscribe(client, topic.c_str());
    esp_mqtt_client_subscribe(client, topic.c_str(), 0);
}

void Mqtt::addCommand(const CommandRegistration &reg)
{
    auto req_size = reg.config->json_size();
    if (req_size > MQTT_RECV_BUFFER_SIZE) {
        logger.printfln("MQTT: Recv buf is %u bytes. %s requires %u. Bump MQTT_RECV_BUFFER_SIZE! Not subscribing!", MQTT_RECV_BUFFER_SIZE, reg.path.c_str(), req_size);
        return;
    }
    if (req_size > (MQTT_RECV_BUFFER_SIZE - MQTT_RECV_BUFFER_HEADROOM))
        logger.printfln("MQTT: Recv buf is %u bytes. %s requires %u. Maybe bump MQTT_RECV_BUFFER_SIZE?", MQTT_RECV_BUFFER_SIZE, reg.path.c_str(), req_size);

    if (mqtt_state.get("connection_state")->asInt() != (int)MqttConnectionState::CONNECTED)
        return;

    subscribe(reg.path, reg.config->json_size(), [reg](char *payload, size_t payload_len){
        String reason = api.getCommandBlockedReason(reg.path);
        if (reason != "") {
            logger.printfln("MQTT: Command %s is blocked: %s", reg.path.c_str(), reason.c_str());
            return;
        }

        String error = reg.config->update_from_cstr(payload, payload_len);
        if(error == "") {
            task_scheduler.scheduleOnce((String("notify command update for ") + reg.path).c_str(), [reg](){reg.callback();}, 0);
            return;
        }

        logger.printfln("MQTT: Failed to update %s from MQTT payload: %s", reg.path.c_str(), error.c_str());
    }, reg.is_action);
}

void Mqtt::addState(const StateRegistration &reg)
{

}

void Mqtt::publish(String payload, String path)
{
    String prefix = mqtt_config_in_use.get("global_topic_prefix")->asString();
    String topic = prefix + "/" + path;
    esp_mqtt_client_publish(this->client, topic.c_str(), payload.c_str(), payload.length(), 0, true/*, false*/);
}

void Mqtt::pushStateUpdate(String payload, String path)
{
    this->publish(payload, path);
}

void Mqtt::wifiAvailable()
{
    static bool started = false;
    if (!started)
        esp_mqtt_client_start(client);
    started = true;
}

void Mqtt::onMqttConnect()
{
    logger.printfln("MQTT: Connected to broker.");
    this->mqtt_state.get("connection_state")->updateInt((int)MqttConnectionState::CONNECTED);

    this->commands.clear();
    for (auto &reg : api.commands) {
        this->addCommand(reg);
    }
    for (auto &reg : api.states) {
        publish(reg.config->to_string_except(reg.keys_to_censor), reg.path);
    }
}

void Mqtt::onMqttDisconnect()
{
    this->mqtt_state.get("connection_state")->updateInt((int)MqttConnectionState::NOT_CONNECTED);
    logger.printfln("MQTT: Disconnected from broker.");
}

void Mqtt::onMqttMessage(char *topic, size_t topic_len, char *data, size_t data_len, bool retain)
{
    for (auto &c : commands) {
        if (c.topic.length() != topic_len)
            continue;
        if (memcmp(c.topic.c_str(), topic, topic_len) != 0)
            continue;

        if (data_len > c.max_len) {
            logger.printfln("MQTT: Ignoring message with payload length %u for topic %s. Maximum length allowed is %u.", data_len, c.topic.c_str(), c.max_len);
            return;
        }

        if (retain && c.forbid_retained) {
            logger.printfln("MQTT: Topic %s is an action. Ignoring retained message.", c.topic.c_str());
            return;
        }

        c.callback(data, data_len);
    }
}

static char err_buf[64] = {0};

static const char *get_mqtt_error(esp_mqtt_connect_return_code_t rc)
{
    switch (rc) {
        case MQTT_CONNECTION_ACCEPTED:
            return "Connection accepted";
        case MQTT_CONNECTION_REFUSE_PROTOCOL:
            return "Wrong protocol";

        case MQTT_CONNECTION_REFUSE_ID_REJECTED:
            return "ID rejected";

        case MQTT_CONNECTION_REFUSE_SERVER_UNAVAILABLE:
            return "Server unavailable";

        case MQTT_CONNECTION_REFUSE_BAD_USERNAME:
            return "Wrong user";

        case MQTT_CONNECTION_REFUSE_NOT_AUTHORIZED:
            return "Wrong username or password";
    }
    return "Unknown error";
}

static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    Mqtt *mqtt = (Mqtt *)handler_args;
    esp_mqtt_event_handle_t event = (esp_mqtt_event_handle_t)event_data;

    switch ((esp_mqtt_event_id_t)event_id) {
        case MQTT_EVENT_CONNECTED:
            task_scheduler.scheduleOnce("mqtt_connected", [mqtt](){
                mqtt->onMqttConnect();
            }, 0);
            break;
        case MQTT_EVENT_DISCONNECTED:
            task_scheduler.scheduleOnce("mqtt_disconnected", [mqtt](){
                mqtt->onMqttDisconnect();
            }, 0);
            break;
        case MQTT_EVENT_DATA:
            if(event->total_data_len != event->data_len) {
                logger.printfln("MQTT: fragmented payload (%u %u). Payload too long?", event->data_len, event->total_data_len);
                return;
            }
            mqtt->onMqttMessage(event->topic, event->topic_len, event->data, event->data_len, event->retain);
            break;
        case MQTT_EVENT_ERROR: {
                auto eh = event->error_handle;

                if (eh->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT) {
                    if (eh->esp_tls_last_esp_err != ESP_OK) {
                        const char *e = esp_err_to_name_r(eh->esp_tls_last_esp_err, err_buf, sizeof(err_buf) / sizeof(err_buf[0]));
                        logger.printfln("MQTT: Transport error: %s (esp_tls_last_esp_err)", e);
                        mqtt->mqtt_state.get("last_error")->updateInt(eh->esp_tls_last_esp_err);
                    }
                    if (eh->esp_tls_stack_err != 0) {
                        const char *e = esp_err_to_name_r(eh->esp_tls_stack_err, err_buf, sizeof(err_buf) / sizeof(err_buf[0]));
                        logger.printfln("MQTT: Transport error: %s (esp_tls_stack_err)", e);
                        mqtt->mqtt_state.get("last_error")->updateInt(eh->esp_tls_stack_err);
                    }
                    if (eh->esp_transport_sock_errno != 0) {
                        const char *e = strerror(eh->esp_transport_sock_errno);
                        logger.printfln("MQTT: Transport error: %s", e);
                        mqtt->mqtt_state.get("last_error")->updateInt(eh->esp_transport_sock_errno);
                    }
                } else if (eh->error_type == MQTT_ERROR_TYPE_CONNECTION_REFUSED) {
                    logger.printfln("MQTT: Connection refused: %s", get_mqtt_error(eh->connect_return_code));
                    // Minus to indicate this is a connection error
                    mqtt->mqtt_state.get("last_error")->updateInt(-eh->connect_return_code);
                } else {
                    logger.printfln("MQTT: Unknown error");
                    mqtt->mqtt_state.get("last_error")->updateInt(0xFFFFFFFF);
                }
                break;
            }
        default:
            break;
    }
}

void Mqtt::setup()
{
    if (!api.restorePersistentConfig("mqtt/config", &mqtt_config)) {
        mqtt_config.get("global_topic_prefix")->updateString(String(BUILD_HOST_PREFIX) + String("/") + String(uid));
        mqtt_config.get("client_name")->updateString(String(BUILD_HOST_PREFIX) + String("-") + String(uid));
    }

    if (!mqtt_config.get("enable_mqtt")->asBool()) {
        initialized = true;
        return;
    }

    api.registerBackend(this);

    esp_log_level_set("MQTT_CLIENT", ESP_LOG_NONE);
    esp_log_level_set("TRANSPORT_BASE", ESP_LOG_NONE);
    esp_log_level_set("esp-tls", ESP_LOG_NONE);
    esp_log_level_set("TRANSPORT", ESP_LOG_NONE);
    esp_log_level_set("OUTBOX", ESP_LOG_NONE);

    mqtt_config_in_use = mqtt_config;

    esp_mqtt_client_config_t mqtt_cfg = {};

    mqtt_cfg.host = mqtt_config_in_use.get("broker_host")->asCStr();
    mqtt_cfg.port = mqtt_config_in_use.get("broker_port")->asUint();
    mqtt_cfg.client_id = mqtt_config_in_use.get("client_name")->asCStr();
    mqtt_cfg.username = mqtt_config_in_use.get("broker_username")->asCStr();
    mqtt_cfg.password = mqtt_config_in_use.get("broker_password")->asCStr();
    mqtt_cfg.buffer_size = MQTT_RECV_BUFFER_SIZE,
    mqtt_cfg.network_timeout_ms = 100;

    client = esp_mqtt_client_init(&mqtt_cfg);
    esp_mqtt_client_register_event(client, (esp_mqtt_event_id_t)ESP_EVENT_ANY_ID, mqtt_event_handler, this);

    initialized = true;
}

void Mqtt::register_urls()
{
    api.addPersistentConfig("mqtt/config", &mqtt_config, {"broker_password"}, 1000);
    api.addState("mqtt/state", &mqtt_state, {}, 1000);
}

void Mqtt::loop()
{

}
