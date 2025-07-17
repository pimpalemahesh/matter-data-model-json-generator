# Copyright 2025 Mahesh Pimpale
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import re

from utils.file_utils import write_to_json_file
# Import file utilities

# Helper functions


def chip_name(name):
    """Convert a name to as per the chip naming convention e.g. On/Off -> OnOff

    :param name:

    """
    name = re.sub(r"[^a-zA-Z0-9]", " ", name)
    words = [word.capitalize() for word in name.split()]
    return "".join(words)


def esp_name(name):
    """Convert a name to as per the esp matter naming convention e.g. On/Off -> on_off

    :param name:

    """
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    return name.lower()


def convert_to_snake_case(name):
    """Convert a name to snake_case. PM2.5 Concentration Measurement -> pm2_5_concentration_measurement

    :param name:

    """
    if name.endswith("Command"):
        name = name[:-7].replace(" ", "_")
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[\/_|\{\}\(\)\\-]", "_", name)
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-zA-Z])([0-9])", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


def check_valid_id(id):
    """Check if an id is valid.

    :param id:

    """
    if id is None or id == "":
        return False
    elif not id.startswith("0x"):
        return False
    elif not is_hex_value(id):
        return False
    if id in ["ID-TBD"]:
        return False
    return True


def safe_get_attr(obj, attr_name, default=None):
    """Safely get an attribute from an object, returning default if attribute doesn't exist

    :param obj: The object to get the attribute from
    :param attr_name: The name of the attribute to get
    :param default: The default value to return if the attribute doesn't exist
    :returns: The attribute value if it exists, otherwise the default value

    """
    return getattr(obj, attr_name, default) if obj else default


def hex_to_int(value):
    """Convert a hex string to an integer.

    :param value:

    """
    if isinstance(value, list):
        return [hex_to_int(v) for v in value]
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 16)
    return value


def is_hex_value(value):
    """Check if a value is a valid hex value e.g. 0x0001

    :param value:

    """
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def format_hex_value(hex_value):
    """Format a hex value by removing unnecessary leading zeros e.g. 0x00000001 -> 0x0001

    :param hex_value: returns: Formatted hex value (e.g., "0x0001")
    :returns: Formatted hex value (e.g., "0x0001")
    :rtype: str

    """
    if hex_value and hex_value.startswith("0x"):
        int_value = int(hex_value, 16)
        return f"0x{int_value:04X}"
    return hex_value
