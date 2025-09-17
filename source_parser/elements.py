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
from source_parser.conformance import Conformance
from utils.attribute_type import AttributeType
from utils.base_elements import *
from utils.helper import safe_get_attr
from utils.logger import setup_logger
from utils.mapping import callback_skip_list

logger = setup_logger()


class Device(BaseDevice):
    """ """

    def __init__(self, id, name, revision):
        super().__init__(id=id, name=name, revision=revision)
        self.clusters = set()
        self.features = set()
        self.commands = set()
        self.attributes = set()
        self.classification = {}
        self.conformance = None
        self.filename = self.esp_name + "_device"

        self.revision_history = []
        self.classification = {}
        self.conditions = []

    def add_feature(self, feature):
        """

        :param feature:

        """
        self.features.add(feature)

    def add_command(self, command):
        """

        :param command:

        """
        self.commands.add(command)

    def add_attribute(self, attribute):
        """

        :param attribute:

        """
        self.attributes.add(attribute)

    def get_clusters(self):
        """ """
        return sorted(self.clusters,
                      key=lambda x:
                      (int(x.get_id(), 16), not x.server_cluster))

    def get_all_mandatory_clusters(self):
        """ """
        mandatory_clusters_with_condition = []
        mandatory_clusters_with_condition.extend(self.get_mandatory_clusters())
        for cluster in self.clusters:
            if cluster.mandatory_with_condition:
                mandatory_clusters_with_condition.append(cluster)
        return sorted(mandatory_clusters_with_condition,
                      key=lambda x:
                      (int(x.get_id(), 16), not x.server_cluster))

    def get_mandatory_clusters(self):
        """ """
        mandatory_clusters = []
        for cluster in self.clusters:
            if cluster.is_mandatory:
                mandatory_clusters.append(cluster)
        return sorted(mandatory_clusters,
                      key=lambda x:
                      (int(x.get_id(), 16), not x.server_cluster))

    def get_unique_clusters(self):
        """ """
        unique_clusters_dict = {}
        for cluster in self.clusters:
            cluster_id = safe_get_attr(cluster, "id")
            if cluster_id not in unique_clusters_dict:
                unique_clusters_dict[cluster_id] = cluster
        unique_clusters = list(unique_clusters_dict.values())
        return sorted(unique_clusters,
                      key=lambda x:
                      (int(x.get_id(), 16), not x.server_cluster))

    def to_dict(self):
        """Convert device object to dictionary representation"""
        from source_parser.serializers import DeviceSerializer

        return DeviceSerializer.to_dict(self)


class Event(BaseEvent):
    """ """

    def __init__(self, id, name, is_mandatory):
        super().__init__(name, id, is_mandatory)
        self.conformance = None

    def is_plain_mandatory(self) -> bool:
        """Check if the event is plain mandatory"""
        if (self.is_mandatory
                    and safe_get_attr(self, "conformance") is not None
                    and safe_get_attr(safe_get_attr(self, "conformance"),
                                      "condition") is None):
            return True
        return False

    def to_dict(self, attribute_map=None):
        """Convert event object to dictionary representation

        :param attribute_map: Default value = None)

        """
        from source_parser.serializers import EventSerializer

        return EventSerializer.to_dict(self, attribute_map)


class Feature(BaseFeature):
    """ """

    def __init__(self, name, code, id):
        super().__init__(name,
                         hex(id) if id is not None else None,
                         is_mandatory=False)
        self.code = code
        self.command_set = set()
        self.attribute_set = set()
        self.event_set = set()
        self.summary = None
        self.conformance = None

    def add_attribute_list(self, attributes: set):
        """Add only mandatory attributes to the feature

        :param attributes: set:
        :param attributes: set:

        """
        if attributes:
            self.attribute_set.update(attributes)

    def get_basic_attributes(self):
        """Returns the list of mandatory attributes for this feature that are not lists, strings or octstrs"""
        attr_list = []
        for attr in self.attribute_set:
            if attr.type not in ["list", "string", "octstr"]:
                attr_list.append(attr)
        if len(attr_list) > 0:
            attr_list.sort(key=lambda x: int(x.get_id(), 16))
        return attr_list

    def add_event_list(self, events: set):
        """Add only mandatory events to the feature

        :param events: set:
        :param events: set:

        """
        if events:
            self.event_set.update(events)

    def get_attribute_list(self):
        """Returns the list of mandatory attributes for this feature"""
        attr_list = list(self.attribute_set)
        if len(attr_list) > 0:
            attr_list.sort(key=lambda x: int(x.get_id(), 16))
        return attr_list

    def get_event_list(self):
        """Returns the list of mandatory events for this feature"""
        event_list = list(self.event_set)
        if len(event_list) > 0:
            event_list.sort(key=lambda x: int(x.get_id(), 16))
        return event_list

    def add_command_list(self, commands):
        """

        :param commands:

        """
        if commands is not None:
            self.command_set.update(commands)

    def get_command_list(self):
        """ """
        command_list = list(self.command_set)
        if len(command_list) > 0:
            command_list.sort(key=lambda x: int(x.get_id(), 16))
        return command_list

    def to_dict(self, attribute_map=None):
        """Convert feature object to dictionary representation

        :param attribute_map: Default value = None)

        """
        from source_parser.serializers import FeatureSerializer

        return FeatureSerializer.to_dict(self, attribute_map)


class Command(BaseCommand):
    """ """

    class CommandFlags:
        """ """

        COMMAND_FLAG_NONE = "COMMAND_FLAG_NONE"
        COMMAND_FLAG_CUSTOM = "COMMAND_FLAG_CUSTOM"
        COMMAND_FLAG_ACCEPTED = "COMMAND_FLAG_ACCEPTED"
        COMMAND_FLAG_GENERATED = "COMMAND_FLAG_GENERATED"

    class CommandAccess:
        """ """

        def __init__(self, invokePrivilege, timed):
            self.invokePrivilege = invokePrivilege
            self.timed = timed

    class CommandField:
        """ """

        def __init__(
            self,
            id,
            name,
            type_,
            default_value=None,
            is_mandatory=False,
            constraint=None,
        ):
            self.id = id
            self.name = name
            self.type = type_
            self.default_value = default_value
            self.is_mandatory = is_mandatory
            self.constraint = constraint

        def to_dict(self):
            """Convert field to dictionary representation"""
            from source_parser.serializers import CommandFieldSerializer

            return CommandFieldSerializer.to_dict(self)

    def __init__(self, id, name, direction, response, is_mandatory):
        super().__init__(
            (name.split(" ")[0] if len(name.split(" ")) > 1
             and name.split(" ")[1] == "Command" else name),
            id,
            is_mandatory,
            direction,
            response,
        )
        self.feature_list = set()
        self.access: self.CommandAccess = None
        self.conformance: Conformance = None
        self.fields = []  # List of CommandField objects
        self.feature_map = {}

        # if command is present in a cluster file with multiple cluster ids e.g. ResourceMonitoring
        self.multi_cluster_command = False
        self.command_handler_available = False

    def set_access(self, access):
        """

        :param access:

        """
        self.access = access

    def set_conformance(self, conformance):
        """

        :param conformance:

        """
        self.conformance = conformance

    def add_field(self, field):
        """

        :param field:

        """
        self.fields.append(field)

    def get_flag(self):
        """ """
        if self.direction and self.direction.lower() == "commandtoserver":
            return self.CommandFlags.COMMAND_FLAG_ACCEPTED
        elif self.direction and self.direction.lower() == "responsefromserver":
            return self.CommandFlags.COMMAND_FLAG_GENERATED
        return self.CommandFlags.COMMAND_FLAG_NONE

    def callback_required(self):
        """Determine if a command requires a callback based on:
        1. Basic command requirements
        2. Conformance complexity


        """
        if self.command_handler_available:
            return False

        # If command is part of a cluster file with multiple cluster ids e.g. ResourceMonitoring
        if self.multi_cluster_command:
            return False

        # If command is in callback_skip_list, then it doesn't need a callback
        if self.name in callback_skip_list:
            return False

        # Skip callbacks for client-bound commands
        if self.direction is not None and self.direction.lower(
        ) != "commandtoserver":
            return False

        # Commands with access privileges typically need callbacks
        if safe_get_attr(self, "access") is not None:
            invoke_privilege = safe_get_attr(safe_get_attr(self, "access"),
                                             "invokePrivilege")

            # Commands with operate/admin/manage privileges or timed=true need callbacks
            if invoke_privilege not in ["operate", "admin", "manage"]:
                return False

        # Commands with response='Y' or specific response commands need callbacks
        if self.response is None or self.response == "N":
            return False

        # Check if this is a response command (ends with 'Response')
        if self.name.endswith("Response"):
            return False

        return True

    def is_plain_mandatory(self) -> bool:
        """Check if the attribute is plain mandatory"""
        if (self.is_mandatory
                    and safe_get_attr(self, "conformance") is not None
                    and safe_get_attr(safe_get_attr(self, "conformance"),
                                      "condition") is None):
            return True
        return False

    def to_dict(self, attribute_map=None):
        """Convert command object to dictionary representation

        :param attribute_map: Default value = None)

        """
        from source_parser.serializers import CommandSerializer

        return CommandSerializer.to_dict(self, attribute_map)


class Attribute(BaseAttribute):
    """ """

    class AttributeFlags:
        """ """

        ATTRIBUTE_FLAG_NONE = "ATTRIBUTE_FLAG_NONE"
        ATTRIBUTE_FLAG_WRITABLE = "ATTRIBUTE_FLAG_WRITABLE"
        ATTRIBUTE_FLAG_NONVOLATILE = "ATTRIBUTE_FLAG_NONVOLATILE"
        ATTRIBUTE_FLAG_MIN_MAX = "ATTRIBUTE_FLAG_MIN_MAX"
        ATTRIBUTE_FLAG_MUST_USE_TIMED_WRITE = "ATTRIBUTE_FLAG_MUST_USE_TIMED_WRITE"
        ATTRIBUTE_FLAG_EXTERNAL_STORAGE = "ATTRIBUTE_FLAG_EXTERNAL_STORAGE"
        ATTRIBUTE_FLAG_SINGLETON = "ATTRIBUTE_FLAG_SINGLETON"
        ATTRIBUTE_FLAG_NULLABLE = "ATTRIBUTE_FLAG_NULLABLE"
        ATTRIBUTE_FLAG_OVERRIDE = "ATTRIBUTE_FLAG_OVERRIDE"
        ATTRIBUTE_FLAG_DEFERRED = "ATTRIBUTE_FLAG_DEFERRED"
        ATTRIBUTE_FLAG_MANAGED_INTERNALLY = "ATTRIBUTE_FLAG_MANAGED_INTERNALLY"

    class Access:
        """ """

        def __init__(self, read, readPrivilege, write, writePrivilege):
            self.read = read
            self.readPrivilege = readPrivilege
            self.write = write
            self.writePrivilege = writePrivilege

    class Quality:
        """ """

        def __init__(
            self,
            changeOmitted,
            nullable,
            scene,
            persistence,
            reportable,
            sourceAttribution=None,
            quieterReporting=None,
        ):
            self.changeOmitted = changeOmitted
            self.nullable = nullable
            self.scene = scene
            self.persistence = persistence
            self.reportable = reportable
            self.sourceAttribution = sourceAttribution
            self.quieterReporting = quieterReporting

    class Constraint:
        """ """

        def __init__(self, type, from_, to_, value):
            self.type = type
            self.from_ = from_
            self.to_ = to_
            self.value = value

        def to_dict(self):
            """Convert constraint to dictionary representation"""
            result = {"type": self.type}

            if not self.type:
                return result

            if self.type == "min":
                if self.value:
                    result["min"] = self.value
            elif self.type == "max":
                if self.value:
                    result["max"] = self.value
            elif self.type == "maxLength":
                if self.value:
                    result["maxLength"] = self.value
            elif self.type == "between":
                if self.from_:
                    result["min"] = self.from_
                if self.to_:
                    result["max"] = self.to_
            elif self.type == "desc":
                if self.value:
                    result["description"] = self.value
            else:
                # For other constraint types
                if self.value:
                    result["value"] = self.value

            return result

    def __init__(
        self,
        name,
        id,
        type_,
        default_value,
        is_mandatory,
        access=None,
        quality=None,
        constraint=None,
    ):
        super().__init__(name, id, type_, is_mandatory, default_value)
        self.conformance: Conformance = None
        self.max_value = None
        self.min_value = None

        # Store access, quality, and constraint information
        self.access = access
        self.quality = quality
        self.constraint = constraint

        self.internally_managed = False

        self.is_nullable = (
            True if safe_get_attr(self, "quality")
            and safe_get_attr(safe_get_attr(self, "quality"), "nullable")
            and safe_get_attr(safe_get_attr(self, "quality"),
                              "nullable").lower() == "true" else False)

    def get_flag(self):
        """Get the flags of the attribute"""
        flags = []
        if safe_get_attr(self, "access"):
            if safe_get_attr(safe_get_attr(self, "access"), "write") and (
                    safe_get_attr(safe_get_attr(self, "access"),
                                  "write").lower() == "true"
                    or safe_get_attr(safe_get_attr(self, "access"),
                                     "write").lower() == "optional"):
                flags.append(self.AttributeFlags.ATTRIBUTE_FLAG_WRITABLE)
            if safe_get_attr(self, "internally_managed"):
                flags.append(
                    self.AttributeFlags.ATTRIBUTE_FLAG_MANAGED_INTERNALLY)

        if safe_get_attr(self, "quality"):
            if (safe_get_attr(safe_get_attr(self, "quality"), "nullable")
                    and safe_get_attr(safe_get_attr(self, "quality"),
                                      "nullable").lower() == "true"):
                flags.append(self.AttributeFlags.ATTRIBUTE_FLAG_NULLABLE)
            if (safe_get_attr(safe_get_attr(self, "quality"), "persistence")
                    and safe_get_attr(safe_get_attr(self, "quality"),
                                      "persistence").lower() == "nonvolatile"):
                flags.append(self.AttributeFlags.ATTRIBUTE_FLAG_NONVOLATILE)
        if len(flags) == 0:
            return self.AttributeFlags.ATTRIBUTE_FLAG_NONE
        return " | ".join(flags)

    def get_default_value_type(self):
        """Get the ESP type for the default value"""
        value = self.get_default_value()
        if value <= 255:
            return "uint8_t"
        elif value <= 65535:
            return "uint16_t"
        return "uint32_t"

    def get_default_value(self):
        """Get the default value of the attribute"""
        return self._convert_default_values()

    def get_type(self):
        """Get the ESP type for the attribute"""
        return AttributeType(self.type).get_attribute_type()

    def _convert_default_values(self):
        """Convert the default value to known values"""
        if self.type == "bool" and self.default_value is not None:
            return "1" if self.default_value.lower() == "true" else "0"

        if self.type == "string" or self.type == "octstr":
            if (safe_get_attr(self, "constraint") is not None
                    and safe_get_attr(safe_get_attr(self, "constraint"),
                                      "type") == "maxLength"
                    and safe_get_attr(safe_get_attr(self, "constraint"),
                                      "value") is not None):
                return int(
                    safe_get_attr(safe_get_attr(self, "constraint"), "value"))
            if self.default_value is not None and self.default_value in [
                    "null",
                    "NULL",
                    "0",
            ]:
                return 0
            return 0

        if self.type == "list":
            if (safe_get_attr(self, "constraint") is not None and
                    safe_get_attr(safe_get_attr(self, "constraint"), "value")
                    and safe_get_attr(safe_get_attr(self, "constraint"),
                                      "value").isdigit()):
                return int(
                    safe_get_attr(safe_get_attr(self, "constraint"), "value"))
            if self.default_value is not None and self.default_value in [
                    "null",
                    "NULL",
                    "0",
                    "empty",
            ]:
                return 0
            return 0

        if "enum" in self.type.lower() or "bitmap" in self.type.lower():
            if self.default_value is not None:
                if self.default_value.isdigit():
                    return int(self.default_value)
                if "0x" in self.default_value:
                    return int(self.default_value, 16)
            return "0"

        if self.default_value is not None and "°" in self.default_value:  # for temperatures
            default_value = self.default_value.split("°")[0]
            if default_value.isdigit():
                return int(default_value) * 100
            return 0

        # for types '123 (0.233)' etc.
        if self.default_value is not None and not self.default_value.isdigit():
            if self.default_value.split(" ")[0].isdigit():
                return int(self.default_value.split(" ")[0])

        if (self.default_value is None and self.constraint is not None
                and self.constraint.value and self.constraint.value.isdigit()
            ):  # if default value is missing
            return int(self.constraint.value)
        return (int(self.default_value) if self.default_value
                and self.default_value.isdigit() else "0")

    def get_max_value(self):
        """Get the max value of the attribute"""
        return self.max_value

    def get_min_value(self):
        """Get the min value of the attribute"""
        return self.min_value

    def is_plain_mandatory(self) -> bool:
        """Check if the attribute is plain mandatory"""
        if (self.is_mandatory
                    and safe_get_attr(self, "conformance") is not None
                    and safe_get_attr(safe_get_attr(self, "conformance"),
                                      "condition") is None):
            return True
        return False

    def to_dict(self, attribute_map=None):
        """Convert attribute object to dictionary representation

        :param attribute_map: Default value = None)

        """
        from source_parser.serializers import AttributeSerializer

        return AttributeSerializer.to_dict(self, attribute_map)


class Cluster(BaseCluster):
    """ """

    class ClusterFlags:
        """ """

        CLUSTER_FLAG_NONE = "CLUSTER_FLAG_NONE"
        CLUSTER_FLAG_INIT_FUNCTION = "CLUSTER_FLAG_INIT_FUNCTION"
        CLUSTER_FLAG_ATTRIBUTE_CHANGED_FUNCTION = "CLUSTER_FLAG_ATTRIBUTE_CHANGED_FUNCTION"
        CLUSTER_FLAG_SHUTDOWN_FUNCTION = "CLUSTER_FLAG_SHUTDOWN_FUNCTION"
        CLUSTER_FLAG_PRE_ATTRIBUTE_CHANGED_FUNCTION = "CLUSTER_FLAG_PRE_ATTRIBUTE_CHANGED_FUNCTION"
        CLUSTER_FLAG_SERVER = "CLUSTER_FLAG_SERVER"
        CLUSTER_FLAG_CLIENT = "CLUSTER_FLAG_CLIENT"

    def __init__(self, name, id, revision):
        super().__init__(name, id, revision, is_mandatory=False)
        self.attributes: set[Attribute] = set()
        self.commands: set[Command] = set()
        self.events: set[Event] = set()
        self.features: set[Feature] = set()
        self.conformance: Conformance = None
        self.revision_history = []
        self.data_types = {}
        # Classification details
        self.role = "application"  # Default value
        self.hierarchy = None
        self.pics_code = None
        self.scope = None
        self.base_cluster_name = None
        self.mandatory_with_condition = False

    def get_attribute_list(self):
        """Get all attributes sorted by attribute id, then by name if ids match"""
        cluster_attributes = list(self.attributes)
        cluster_attributes.sort(key=lambda x: (int(x.get_id(), 16), x.name))
        return cluster_attributes

    def get_command_list(self):
        """Get all commands sorted by command id, then by name if ids match"""
        cluster_commands = list(self.commands)
        cluster_commands.sort(key=lambda x: (int(x.get_id(), 16), x.name))
        return cluster_commands

    def get_event_list(self):
        """Get all events sorted by event id, then by name if ids match"""
        cluster_events = list(self.events)
        cluster_events.sort(key=lambda x: (int(x.get_id(), 16), x.name))
        return cluster_events

    def get_feature_list(self):
        """Get all features sorted by feature id"""
        cluster_features = list(self.features)
        cluster_features.sort(key=lambda x: int(x.get_id(), 16))
        return cluster_features

    def get_feature_choice_list(self) -> list[Feature]:
        """Get the list of features with optional conformance and choice attributes sorted by feature id


        :returns: A list of features with optional conformance and choice attributes sorted by feature id.

        """
        choice_features = []
        dependent_features = set(
        )  # Features that are dependencies of choice features

        for feature in self.features:
            conformance = safe_get_attr(feature, "conformance")
            is_choice_feature = False

            # Check for direct optional conformance with choice
            if (conformance
                    and safe_get_attr(conformance, "type") == "optional"
                    and safe_get_attr(conformance, "choice") is not None):
                choice_features.append(feature)
                is_choice_feature = True

            # Check for otherwise conformance with optional choice condition
            elif (conformance
                  and safe_get_attr(conformance, "type") == "otherwise"
                  and safe_get_attr(conformance, "condition") is not None):
                condition = safe_get_attr(conformance, "condition")
                if (isinstance(condition, dict) and "optional" in condition
                        and isinstance(condition["optional"], dict)
                        and "choice" in condition["optional"]):
                    choice_features.append(feature)
                    is_choice_feature = True

                    # Also check for mandatory dependencies within the same otherwise conformance
                    if "mandatory" in condition and isinstance(
                            condition["mandatory"], dict):
                        if "feature" in condition["mandatory"]:
                            feature_name = condition["mandatory"]["feature"]
                            dependent_features.add(feature_name)

        # Find the actual feature objects for the dependent features
        for feature in self.features:
            feature_func_name = safe_get_attr(feature, "func_name", "")
            if feature_func_name in dependent_features:
                choice_features.append(feature)

        # Remove duplicates while preserving order
        unique_choice_features = []
        seen = set()
        for feature in choice_features:
            if feature not in seen:
                unique_choice_features.append(feature)
                seen.add(feature)

        if len(unique_choice_features) > 0:
            unique_choice_features.sort(key=lambda x: int(x.get_id(), 16))
        return unique_choice_features

    def get_mandatory_attributes(self):
        """Get only mandatory attributes from the attribute list"""
        """note: This also includes the mandatory attributes with conformance conditions as either not or which has conformance condition string as None"""
        mandatory_attributes = []
        for attribute in self.attributes:
            if (attribute.is_mandatory
                    and safe_get_attr(attribute, "conformance") is not None
                    and safe_get_attr(safe_get_attr(attribute, "conformance"),
                                      "condition") is None):
                mandatory_attributes.append(attribute)
        if len(mandatory_attributes) > 0:
            mandatory_attributes.sort(
                key=lambda x: (int(x.get_id(), 16), x.name))
        return mandatory_attributes

    def get_mandatory_commands(self):
        """Get only mandatory commands from the command list"""
        """note: This also includes the mandatory commands with conformance conditions as either not or which has conformance condition string as None"""
        mandatory_commands = []
        for command in self.commands:
            if (command.is_mandatory
                    and safe_get_attr(command, "conformance") is not None
                    and safe_get_attr(safe_get_attr(command, "conformance"),
                                      "condition") is None):
                mandatory_commands.append(command)
        if len(mandatory_commands) > 0:
            mandatory_commands.sort(
                key=lambda x: (int(x.get_id(), 16), x.name))
        return mandatory_commands

    def get_mandatory_events(self):
        """Get only mandatory events from the event list"""
        """note: This also includes the mandatory events with conformance conditions as either not or which has conformance condition string as None"""
        mandatory_events = []
        for event in self.events:
            if (event.is_mandatory
                    and safe_get_attr(event, "conformance") is not None
                    and safe_get_attr(safe_get_attr(event, "conformance"),
                                      "condition") is None):
                mandatory_events.append(event)
        if len(mandatory_events) > 0:
            mandatory_events.sort(key=lambda x: (int(x.get_id(), 16), x.name))
        return mandatory_events

    def get_mandatory_features(self):
        """Get only mandatory features from the feature list"""
        """note: This method is not implemented yet"""
        return list(self.features)

    def get_basic_mandatory_attributes(self):
        """Get only mandatory attributes from the attribute list that are not list, string, or octstr"""
        basic_mandatory_attributes = list(
            attribute for attribute in self.get_mandatory_attributes()
            if attribute.type not in ["list", "string", "octstr"])
        if len(basic_mandatory_attributes) > 0:
            basic_mandatory_attributes.sort(key=lambda x: int(x.get_id(), 16))
        return basic_mandatory_attributes

    def get_function_flags(self):
        """Get the function flags for the cluster"""
        flags = []
        if self.server_cluster:
            flags.append(self.ClusterFlags.CLUSTER_FLAG_SERVER)
        if self.client_cluster:
            flags.append(self.ClusterFlags.CLUSTER_FLAG_CLIENT)
        if self.init_function_available:
            flags.append(self.ClusterFlags.CLUSTER_FLAG_INIT_FUNCTION)
        if self.attribute_changed_function_available:
            flags.append(
                self.ClusterFlags.CLUSTER_FLAG_ATTRIBUTE_CHANGED_FUNCTION)
        if self.shutdown_function_available:
            flags.append(self.ClusterFlags.CLUSTER_FLAG_SHUTDOWN_FUNCTION)
        if self.pre_attribute_change_function_available:
            flags.append(
                self.ClusterFlags.CLUSTER_FLAG_PRE_ATTRIBUTE_CHANGED_FUNCTION)

        if len(flags) > 0:
            return " | ".join(flags)
        return self.ClusterFlags.CLUSTER_FLAG_NONE

    def get_string_attributes(self):
        """Get list of string attributes with length constraints"""
        return [
            attr for attr in self.attributes if attr.type == "string"
            and safe_get_attr(attr, "max_length") is not None
        ]

    def to_dict(self):
        """Convert cluster object to dictionary representation"""
        from source_parser.serializers import ClusterSerializer

        return ClusterSerializer.to_dict(self)
