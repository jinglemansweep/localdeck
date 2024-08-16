#!/usr/bin/env python3

import re
import yaml
from typing import List, Dict

MATRIX_ROW_COUNT = 4
MATRIX_COLUMN_COUNT = 6
MATRIX_BUTTON_COUNT = MATRIX_ROW_COUNT * MATRIX_COLUMN_COUNT


def replace_secret_strings(text: str) -> str:
    pattern = re.compile(r"__secret[ ](\w+)")
    return pattern.sub(r"!secret \1", text)


binary_sensors: List[Dict] = [
    {
        "platform": "gpio",
        "id": "keypad_row_21",
        "pin": {"number": "GPIO21", "allow_other_uses": True},
    },
    {
        "platform": "gpio",
        "id": "keypad_row_20",
        "pin": {"number": "GPIO20", "allow_other_uses": True},
    },
    {
        "platform": "gpio",
        "id": "keypad_row_03",
        "pin": {"number": "GPIO3", "allow_other_uses": True},
    },
    {
        "platform": "gpio",
        "id": "keypad_row_07",
        "pin": {"number": "GPIO7", "allow_other_uses": True},
    },
]

lights: List[Dict] = [
    {
        "platform": "esp32_rmt_led_strip",
        "name": "Ledstrip",
        "id": "ledstrip",
        "rgb_order": "GRB",
        "pin": "GPIO8",
        "rmt_channel": 0,
        "num_leds": MATRIX_BUTTON_COUNT,
        "chipset": "SK6812",
        "restore_mode": "RESTORE_AND_OFF",
        "effects": [],
    }
]


config: Dict = {
    "substitutions": {
        "name": "localdeck",
        "friendly_name": "LocalDeck MQTT",
    },
    "esphome": {
        "name": "localdeck",
        "friendly_name": "LocalDeck MQTT",
        "platformio_options": {"board_build.flash_mode": "dio"},
    },
    "esp32": {
        "board": "esp32-c3-devkitm-1",
        "framework": {"type": "esp-idf", "sdkconfig_options": {}},
    },
    "logger": {},
    "ota": {"platform": "esphome", "password": "__secret ota_password"},
    "api": {},
    "wifi": {
        "ssid": "__secret wifi_ssid",
        "password": "__secret wifi_password",
        "power_save_mode": "NONE",
    },
    "captive_portal": {},
    "mqtt": {
        "broker": "__secret mqtt_broker",
        "port": "__secret mqtt_port",
        "username": "__secret mqtt_username",
        "password": "__secret mqtt_password",
        "log_topic": None,
    },
    "light": lights,
    "binary_sensor": binary_sensors,
    "matrix_keypad": {
        "id": "keypad",
        "keys": "ABCDEFGHIJKLMNOPQRSTUVWX",
        "rows": [
            {"pin": {"number": "GPIO21", "allow_other_uses": True}},
            {"pin": {"number": "GPIO20", "allow_other_uses": True}},
            {"pin": {"number": "GPIO3", "allow_other_uses": True}},
            {"pin": {"number": "GPIO7", "allow_other_uses": True}},
        ],
        "columns": [
            {"pin": "GPIO0"},
            {"pin": "GPIO1"},
            {"pin": "GPIO10"},
            {"pin": "GPIO4"},
            {"pin": "GPIO5"},
            {"pin": "GPIO6"},
        ],
    },
}

matrix_keymap = [
    18,
    19,
    20,
    21,
    22,
    23,
    12,
    13,
    14,
    15,
    16,
    17,
    6,
    7,
    8,
    9,
    10,
    11,
    0,
    1,
    2,
    3,
    4,
    5,
]


for i in range(0, MATRIX_BUTTON_COUNT):
    ri = matrix_keymap[i]
    li = ri + 1
    config["light"].append(
        {
            "platform": "partition",
            "id": f"keypad_button_{li:02d}_light",
            "name": f"Button {li:02d} Light",
            "internal": False,
            "segments": [{"id": "ledstrip", "from": ri, "to": ri}],
        }
    )

    config["binary_sensor"].append(
        {
            "platform": "matrix_keypad",
            "id": f"keypad_button_{li:02d}",
            "name": f"Button {li:02d}",
            "internal": False,
            "keypad_id": "keypad",
            "key": chr(65 + i),
            "on_press": [],
            "on_click": [],
            "on_double_click": [],
            "on_multi_click": [],
        }
    )

output = yaml.dump(config)
output = replace_secret_strings(output)

print(output)
