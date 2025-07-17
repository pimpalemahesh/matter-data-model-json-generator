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


class AttributeType:
    """ """

    _basic_types = {
        "bool": "bool",
        "uint8": "uint8_t",
        "uint16": "uint16_t",
        "uint32": "uint32_t",
        "uint64": "uint64_t",
        "int8": "int8_t",
        "int16": "int16_t",
        "int32": "int32_t",
        "int64": "int64_t",
        "float": "float",
        "double": "double",
    }

    _string_type = {"string": "char *", "octstr": "uint8_t *"}

    _array_type = {"list": "uint8_t *"}

    _enum_type = {
        "enum8": "uint8_t",
        "enum16": "uint16_t",
        "enum32": "uint32_t",
        "enum64": "uint64_t",
    }

    _bitmap_type = {
        "bitmap8": "uint8_t",
        "bitmap16": "uint16_t",
        "bitmap32": "uint32_t",
        "bitmap64": "uint64_t",
    }

    def __init__(self, type_str: str):
        self.type_str = type_str

    def get_attribute_type(self) -> str:
        """Get the attribute type for a given type string
        The attribute types are converted from cpp type to the types used in esp-matter.


        :returns: The attribute type.

        """
        if self.type_str in self._basic_types:
            return self._basic_types[self.type_str]
        elif self.type_str in self._string_type:
            return self._string_type[self.type_str]
        elif self.type_str in self._array_type:
            return self._array_type[self.type_str]
        elif self.type_str in self._enum_type:
            return self._enum_type[self.type_str]
        elif self.type_str in self._bitmap_type:
            return self._bitmap_type[self.type_str]
        else:
            raise ValueError(f"Could not resolve type: {self.type_str}")

    def get_attribute_category(self) -> str:
        """Get the attribute category for a given type string


        :returns: The attribute category.

        """
        if self.type_str in self._basic_types:
            return "PRIMITIVE"
        elif self.type_str in self._string_type:
            return "STRING"
        elif self.type_str in self._array_type:
            return "ARRAY"
        elif self.type_str in self._enum_type:
            return "ENUM"
        elif self.type_str in self._bitmap_type:
            return "BITMAP"
        else:
            return "UNKNOWN"


attribute_type_map = {
    "Alarm_Base": {
        "Mask": {
            "type": "bitmap32",
            "min": "0",
            "max": "4294967295",
        },
        "Latch": {
            "type": "bitmap32",
            "min": "0",
            "max": "4294967295",
        },
        "State": {
            "type": "bitmap32",
            "min": "0",
            "max": "4294967295",
        },
        "Supported": {
            "type": "bitmap32",
            "min": "0",
            "max": "4294967295",
        },
    }
}

# Global attribute mapping xml-type -> cpp->type
attribute_types = {
    # PRIMITIVE
    "uint8": "uint8",
    "uint16": "uint16",
    "uint32": "uint32",
    "uint64": "uint64",
    "int8": "int8",
    "int16": "int16",
    "int32": "int32",
    "int64": "int64",
    "float": "float",
    "double": "double",
    "string": "string",
    "octstr": "octstr",
    "list": "list",
    "bool": "bool",
    "enum8": "enum8",
    "enum16": "enum16",
    "enum32": "enum32",
    "enum64": "enum64",
    "bitmap8": "bitmap8",
    "bitmap16": "bitmap16",
    "bitmap32": "bitmap32",
    "bitmap64": "bitmap64",
    "struct": "list",
    "percent": "uint8",
    "percent100ths": "uint16",
    "tod": "list",
    "date": "list",
    "epoch-us": "uint64",
    "epoch-s": "uint32",
    "utc": "uint32",
    # DERIVED
    # ANALOG
    "posix-ms": "uint64",
    "systime-us": "uint64",
    "systime-ms": "uint64",
    "elapsed-s": "uint32",
    # Physical Quantities
    "temperature": "int16",
    "power-mw": "int64",
    "amperage-ma": "int64",
    "voltage-mv": "int64",
    "energy-mwh": "int64",
    "power-mva": "int64",
    "energy-mvah": "int64",
    "power-mvar": "int64",
    "energy-mvarh": "int64",
    "money": "int64",
    "tempdiff": "int16",
    "utemp": "uint8",
    "stemp": "int8",
    # DISCRETE
    "priority": "uint8",
    "status": "uint8",
    "group-id": "uint16",
    "endpoint-id": "uint16",
    "endpoint-no": "uint16",
    "vendor-id": "uint16",
    "devtype-id": "uint32",
    "fabric-id": "uint64",
    "fabric-idx": "uint8",
    "cluster-id": "uint32",
    "attrib-id": "uint32",
    "field-id": "uint32",
    "event-id": "uint32",
    "command-id": "uint32",
    "action-id": "uint8",
    "subject-id": "uint32",
    "trans-id": "uint32",
    "node-id": "uint64",
    "EUI64": "uint64",
    "entry-idx": "uint16",
    "data-ver": "uint32",
    "event-no": "uint64",
    # COMPOSITE
    "string": "string",
    "octstr": "octstr",
    # address
    "ipadr": "octstr",
    "ipv4adr": "octstr",
    "ipv6adr": "octstr",
    "ipv6pre": "octstr",
    "hwadr": "octstr",
    # tag
    "semtag": "list",
    "namespace": "enum8",
    "tag": "enum8",
    # location
    "locationdesc": "list",
    # Custom (not in the spec)
    # Temperature
    "signedtemperature": "int8",
    "unsignedtemperature": "uint8",
    "temperaturedifference": "int16",
    "temperature": "int16",
    # Additional types
    "unknown": "unknown",
    "custom": "custom",
    "map8": "bitmap8",
    "map16": "bitmap16",
    "map32": "bitmap32",
    "map64": "bitmap64",
    "uint24": "uint32",
    "uint40": "uint64",
    "uint48": "uint64",
    "uint56": "uint64",
    "int24": "int32",
    "int40": "int64",
    "int48": "int64",
    "int56": "int64",
    "int8s": "int8",
    "int16s": "int16",
    "int32s": "int32",
    "int64s": "int64",
    "single": "float",
    "message-id": "uint32",
    "mode": "bool",
    "boolean": "bool",
    "min": "uint8",  # Not sure
    "max": "uint8",  # Not sure
    "datatypelist[ref_groupkeysetstruct]": "list",
    "datatypelist[datastore": "list",
    "datastore": "list",
}
