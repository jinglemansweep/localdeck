#!/usr/bin/env python3

import re
import yaml
from typing import List, Dict

MATRIX_ROW_COUNT = 4
MATRIX_COLUMN_COUNT = 6
MATRIX_BUTTON_COUNT = MATRIX_ROW_COUNT * MATRIX_COLUMN_COUNT


config_binary_sensors: List[Dict] = [
    dict(platform="gpio", id="keypad_row_21", pin={"number": "GPIO21", "allow_other_uses": True}),
    dict(platform="gpio", id="keypad_row_20", pin={"number": "GPIO20", "allow_other_uses": True}),
    dict(platform="gpio", id="keypad_row_03", pin={"number": "GPIO3", "allow_other_uses": True}),
    dict(platform="gpio", id="keypad_row_07", pin={"number": "GPIO7", "allow_other_uses": True}),
]
config_lights: List[Dict] = [
    dict(
        platform="esp32_rmt_led_strip",
        name="Ledstrip",
        id="ledstrip",
        rgb_order="GRB",
        pin="GPIO8",
        rmt_channel=0,
        num_leds=MATRIX_BUTTON_COUNT,
        chipset="SK6812",
        restore_mode="RESTORE_AND_OFF",
        effects=[],
    )
]
config_switches: List[Dict] = [dict(platform="restart", name="Restart")]
config_text_sensors: List[Dict] = [dict(platform="wifi_info", mac_address=dict(id="wifi_info_mac_address"))]


config_all: Dict = dict(
    substitutions=dict(
        name="localdeck",
        friendly_name="LocalDeck",
    ),
    esphome=dict(
        name="${name}",
        friendly_name="${friendly_name}",
        platformio_options=dict(board_build_flash_mode="dio"),
    ),
    esp32=dict(
        board="esp32-c3-devkitm-1",
        framework=dict(type="esp-idf", sdkconfig_options={}),
    ),
    logger=dict(),
    ota=dict(platform="esphome", password="__secret ota_password"),
    api=dict(),
    wifi=dict(
        ap=dict(ssid="${friendly_name} AP"),
        ssid="__secret wifi_ssid",
        password="__secret wifi_password",
        power_save_mode="NONE",
    ),
    captive_portal=dict(),
    matrix_keypad=dict(
        id="keypad",
        keys="ABCDEFGHIJKLMNOPQRSTUVWX",
        rows=[
            dict(pin=dict(number="GPIO21", allow_other_uses=True)),
            dict(pin=dict(number="GPIO20", allow_other_uses=True)),
            dict(pin=dict(number="GPIO3", allow_other_uses=True)),
            dict(pin=dict(number="GPIO7", allow_other_uses=True)),
        ],
        columns=[
            dict(pin="GPIO0"),
            dict(pin="GPIO1"),
            dict(pin="GPIO10"),
            dict(pin="GPIO4"),
            dict(pin="GPIO5"),
            dict(pin="GPIO6"),
        ],
    ),
    binary_sensor=config_binary_sensors,
    light=config_lights,
    switch=config_switches,
    text_sensor=config_text_sensors,
)


def get_key_index(columns, rows, index, invert_y=False):
    x = index % columns
    y = index // columns
    y_abs = rows - 1 - y if invert_y else y
    new_index = y_abs * columns + x
    return new_index


def replace_secret_strings(text: str) -> str:
    pattern = re.compile(r"__secret[ ](\w+)")
    return pattern.sub(r"!secret \1", text)


def build_ledstrip_light(idx: int):
    fmt = f"{idx + 1:02d}"
    return dict(
        platform="partition",
        id=f"keypad_button_{fmt}_light",
        name=f"Button {fmt} Light",
        internal=False,
        segments=[
            {
                "id": "ledstrip",
                "from": idx,
                "to": idx,
            }
        ],
    )


def build_binary_sensor(idx: int):
    fmt = f"{idx + 1:02d}"
    return dict(
        platform="matrix_keypad",
        id=f"keypad_button_{fmt}",
        name=f"Button {fmt}",
        internal=False,
        keypad_id="keypad",
        key=chr(65 + idx),
        on_press=[],
        on_click=[],
        on_double_click=[],
        on_multi_click=[],
    )


def build_text_sensor(idx: int, entity_id: str):
    fmt = f"{idx + 1:02d}"
    return dict(
        platform="homeassistant",
        id=f"keypad_button_{fmt}_hass",
        entity_id=entity_id,
        on_value=[
            dict(
                platform="light.control",
                id=f"keypad_button_{fmt}_light",
                state="!lambda return x == 'on';",
            )
        ],
    )


config = config_all.copy()

for i in range(0, MATRIX_BUTTON_COUNT):
    i_flipped = get_key_index(MATRIX_COLUMN_COUNT, MATRIX_ROW_COUNT, i, invert_y=True)
    config["binary_sensor"].append(build_binary_sensor(i_flipped))
    config["light"].append(build_ledstrip_light(i))
    config["text_sensor"].append(build_text_sensor(i_flipped, ""))


output = yaml.dump(config, sort_keys=False)
output = replace_secret_strings(output)

print(output)
