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
from utils.attribute_type import attribute_types
from utils.helper import safe_get_attr
from utils.logger import setup_logger

logger = setup_logger()


class Item:
    """ """

    def __init__(self, name, value, summary, is_mandatory):
        self.name = name
        self.value = value
        self.summary = summary
        self.is_mandatory = is_mandatory

    def to_dict(self):
        """ """
        return {
            "name": self.name,
            "value": self.value,
            "summary": self.summary,
            "is_mandatory": self.is_mandatory,
        }


class Enum:
    """ """

    def __init__(self, name, base_type, items):
        self.name: str = name
        self.base_type: str = base_type
        self.items: list[Item] = items

    def to_dict(self):
        """ """
        return {
            "name": self.name,
            "base_type": self.base_type,
            "items": [item.to_dict() for item in self.items],
        }


class Bitmap:
    """ """

    def __init__(self, name, base_type, bitfields):
        self.name: str = name
        self.base_type: str = base_type
        self.bitfields: list[Item] = bitfields

    def to_dict(self):
        """ """
        return {
            "name": self.name,
            "base_type": self.base_type,
            "bitfields": [bitfield.to_dict() for bitfield in self.bitfields],
        }


class Struct:
    """ """

    def __init__(self, name, base_type, fields):
        self.name: str = name
        self.base_type: str = base_type
        self.fields: list[Item] = fields

    def to_dict(self):
        """ """
        return {
            "name": self.name,
            "base_type": self.base_type,
            "fields": [field.to_dict() for field in self.fields],
        }


class DataTypeParser:
    """ """

    def __init__(self):
        self.attribute_types = attribute_types
        self.enums = {}
        self.bitmaps = {}
        self.structs = {}

    def parse_data_types(self, root):
        """Parse dataTypes section and create type mapping

        :param root: returns: A dictionary of data types.
        :returns: A dictionary of data types.

        """
        data_types = root.find("dataTypes")
        if data_types is not None:
            # Parse enums - count items
            for enum in data_types.findall("enum"):
                enum_name = enum.get("name").lower()
                attribute_types[enum_name] = self.get_enum_type(enum)

                # Store complete enum information
                self.enums[enum_name] = Enum(
                    enum.get("name"),
                    attribute_types[enum_name],
                    [
                        Item(
                            item.get("name"),
                            item.get("value"),
                            item.get("summary"),
                            item.find("mandatoryConform") is not None,
                        ) for item in enum.findall("item")
                    ],
                )

            # Parse bitmaps - check highest bit position
            for bitmap in data_types.findall("bitmap"):
                bitmap_name = bitmap.get("name").lower()
                attribute_types[bitmap_name] = self.get_bitmap_type(bitmap)

                # Store complete bitmap information
                self.bitmaps[bitmap_name] = Bitmap(
                    bitmap.get("name"),
                    attribute_types[bitmap_name],
                    [
                        Item(
                            safe_get_attr(bitfield, "name"),
                            safe_get_attr(bitfield, "bit"),
                            safe_get_attr(bitfield, "summary"),
                            bitfield.find("mandatoryConform") is not None,
                        ) for bitfield in bitmap.findall("bitfield")
                    ],
                )

            # Parse structs - check number of fields
            for struct in data_types.findall("struct"):
                struct_name = struct.get("name").lower()
                attribute_types[struct_name] = "list"

                # Store complete struct information
                self.structs[struct_name] = Struct(
                    struct.get("name"),
                    "list",
                    [
                        Item(
                            safe_get_attr(field, "name"),
                            safe_get_attr(field, "type"),
                            safe_get_attr(field, "summary"),
                            field.find("mandatoryConform") is not None,
                        ) for field in struct.findall("field")
                    ],
                )

        return attribute_types

    def get_enum_type(self, enum_element):
        """Infer enum type based on number of items

        :param enum_element: returns: The enum type.
        :returns: The enum type.

        """
        item_count = len(enum_element.findall("item"))
        if item_count <= 255:
            return "enum8"
        elif item_count <= 65535:
            return "enum16"
        else:
            return "enum32"

    def get_bitmap_type(self, bitmap_element):
        """Infer bitmap type based on highest bit position

        :param bitmap_element: returns: The bitmap type.
        :returns: The bitmap type.

        """
        max_bit = len(bitmap_element.findall("bitfield"))
        if max_bit < 8:
            return "bitmap8"
        elif max_bit < 16:
            return "bitmap16"
        else:
            return "bitmap32"

    def get_enum_type_from_value(self, default_value):
        """Get enum type from default value

        :param default_value: returns: The enum type.
        :returns: The enum type.

        """
        if default_value <= 255:
            return "enum8"
        elif default_value <= 65535:
            return "enum16"
        else:
            return "enum32"

    def get_bitmap_type_from_value(self, default_value):
        """Get bitmap type from default value

        :param default_value: returns: The bitmap type.
        :returns: The bitmap type.

        """
        if default_value <= 255:
            return "bitmap8"
        elif default_value <= 65535:
            return "bitmap16"
        else:
            return "bitmap32"

    def get_data_types(self):
        """Return all parsed data types


        :returns: A dictionary of data types.

        """
        return {
            "enums": self.enums,
            "bitmaps": self.bitmaps,
            "structs": self.structs
        }
