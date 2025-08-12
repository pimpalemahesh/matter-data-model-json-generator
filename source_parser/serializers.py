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
"""
Serializer classes to convert source parser elements to dictionary representations.
This helps separate serialization logic from the data classes.
"""
from source_parser.data_type_parser import Bitmap
from source_parser.data_type_parser import Enum
from source_parser.data_type_parser import Struct
from utils.helper import safe_get_attr


class DataTypeSerializer:
    """ """

    @staticmethod
    def to_dict(data_types):
        """Convert a DataType object to dictionary representation

        :param data_type:
        :param data_types:

        """
        parsed = {}
        for data_type, data_type_list in data_types.items():
            type_list = []
            for data_type_name, data_type_object in data_type_list.items():
                type_list.append(data_type_object.to_dict())
            parsed[data_type] = type_list
        return parsed


class AttributeSerializer:
    """ """

    @staticmethod
    def to_dict(attr, attribute_map=None):
        """Convert an Attribute object to dictionary representation

        :param attr: param attribute_map:  (Default value = None)
        :param attribute_map:  (Default value = None)

        """
        return {
            "name": safe_get_attr(attr, "name"),
            "id": safe_get_attr(attr, "id"),
        }


class CommandSerializer:
    """ """

    @staticmethod
    def to_dict(cmd, attribute_map=None):
        """Convert a Command object to dictionary representation

        :param cmd: param attribute_map:  (Default value = None)
        :param attribute_map:  (Default value = None)

        """
        return {
            "name": safe_get_attr(cmd, "name"),
            "id": safe_get_attr(cmd, "id"),
        }


class EventSerializer:
    """ """

    @staticmethod
    def to_dict(event, attribute_map=None):
        """Convert an Event object to dictionary representation

        :param event: param attribute_map:  (Default value = None)
        :param attribute_map:  (Default value = None)

        """
        return {
            "name": safe_get_attr(event, "name"),
            "id": event.get_id(),
        }


class FeatureSerializer:
    """ """

    @staticmethod
    def to_dict(feature, attribute_map=None):
        """Convert a Feature object to dictionary representation

        :param feature: param attribute_map:  (Default value = None)
        :param attribute_map:  (Default value = None)

        """
        return {
            "name":
            safe_get_attr(feature, "name"),
            "id":
            feature.get_id(),
            "code":
            safe_get_attr(feature, "code"),
            "required": False,
            "attributes": [
                AttributeSerializer.to_dict(attr, attribute_map)
                for attr in feature.get_attribute_list()
            ],
            "commands": [
                CommandSerializer.to_dict(cmd, attribute_map)
                for cmd in feature.get_command_list()
            ],
            "events": [
                EventSerializer.to_dict(event, attribute_map)
                for event in feature.get_event_list()
            ],
        }


class ClusterSerializer:
    """ """

    @staticmethod
    def to_dict(cluster):
        """Convert a Cluster object to dictionary representation

        :param cluster:

        """
        # Create attribute map (attribute name -> ID)
        attribute_map = {}
        for attr in (cluster.get_attribute_list() if hasattr(
                cluster, "get_attribute_list") else safe_get_attr(
                    cluster, "attributes", [])):
            attribute_map[safe_get_attr(
                attr, "name")] = (attr.get_id() if hasattr(attr, "get_id") else
                                  safe_get_attr(attr, "id"))

        # Create command map (command name -> ID)
        command_map = {}
        for cmd in (cluster.get_command_list() if hasattr(
                cluster, "get_command_list") else safe_get_attr(
                    cluster, "commands", [])):
            command_map[safe_get_attr(
                cmd, "name")] = ((cmd.get_id(), cmd.get_flag()) if hasattr(
                    cmd, "get_id") else safe_get_attr(cmd, "id"))

        # Merge attribute and command maps for conformance usage
        reference_map = {**attribute_map, **command_map}

        return {
            "name":
            safe_get_attr(cluster, "name"),
            "id":
            cluster.get_id(),
            "revision":
            cluster.get_revision(),
            "required": False,
            "attributes": [
                AttributeSerializer.to_dict(attr, reference_map)
                for attr in cluster.get_mandatory_attributes()
            ],
            "commands": [
                CommandSerializer.to_dict(cmd, reference_map)
                for cmd in cluster.get_mandatory_commands()
            ],
            "events": [
                EventSerializer.to_dict(event, reference_map)
                for event in cluster.get_mandatory_events()
            ],
            "features": [
                FeatureSerializer.to_dict(feature, reference_map)
                for feature in cluster.get_mandatory_features()
            ],
        }


class DeviceSerializer:
    """ """

    @staticmethod
    def to_dict(device):
        """Convert a Device object to dictionary representation

        :param device:

        """
        result = {
            "name":
            safe_get_attr(device, "name"),
            "id":
            device.get_id(),
            "revision":
            safe_get_attr(device, "revision"),
            "clusters": [{
                "name":
                safe_get_attr(cluster, "name"),
                "id":
                cluster.get_id(),
                "type":
                ("server" if safe_get_attr(cluster, "server_cluster") else
                 ("client"
                  if safe_get_attr(cluster, "client_cluster") else None)),
                "required": True if cluster.is_mandatory else "conditional" if cluster.mandatory_with_condition else False,
                "features":
                safe_get_attr(cluster, "feature_name_list", []),
                "commands":
                safe_get_attr(cluster, "command_name_list", []),
                "attributes":
                safe_get_attr(cluster, "attribute_name_list", []),
            } for cluster in device.get_all_mandatory_clusters()],
        }
        return result


class CommandFieldSerializer:
    """ """

    @staticmethod
    def to_dict(field):
        """Convert CommandField object to dictionary representation

        :param field:

        """
        if not field:
            return None

        result = {
            "id": safe_get_attr(field, "id"),
            "name": safe_get_attr(field, "name"),
            "type": safe_get_attr(field, "type"),
            "mandatory": safe_get_attr(field, "is_mandatory"),
        }

        default_value = safe_get_attr(field, "default_value")
        if default_value:
            result["default_value"] = default_value

        constraint = safe_get_attr(field, "constraint")
        if constraint:
            # If constraint is already a dict, just use it
            if isinstance(constraint, dict):
                result["constraint"] = constraint
            # Otherwise try to convert it
            elif hasattr(constraint, "to_dict"):
                result["constraint"] = constraint.to_dict()

        return result
