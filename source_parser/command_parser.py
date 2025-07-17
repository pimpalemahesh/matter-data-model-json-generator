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
from source_parser.conformance import parse_conformance
from source_parser.conformance import parse_otherwise_conformance
from source_parser.elements import Cluster
from source_parser.elements import Command
from source_parser.yaml_parser import YamlParser
from utils.helper import check_valid_id
from utils.helper import safe_get_attr
from utils.logger import setup_logger
from utils.mapping import command_callback_skip_list

logger = setup_logger()


class CommandParser:
    """Class for parsing command data"""

    def __init__(
        self,
        cluster: Cluster,
        feature_map: dict,
    ):
        self.cluster = cluster
        self.feature_map = feature_map if feature_map else {}
        self.processed_commands = set()

    def parse_commands(self, root, base_commands: list[Command] = None):
        """Iterate over all command elements in the cluster xml file and create Command objects.

        :param root: The root element of the cluster XML file.
        :param base_commands: The base commands.
        :param base_commands: list[Command]:  (Default value = None)
        :param base_commands: list[Command]:  (Default value = None)

        """
        for command in root.findall("commands/command"):
            if not self._should_process_command(command, base_commands):
                continue

            cmd = self._create_command(command)
            self._process_command_access(cmd, command)
            self._process_command_conformance(cmd, command)
            self._process_command_fields(cmd, command)

            self.cluster.commands.add(cmd)

            if safe_get_attr(self.cluster,
                             "esp_name") in command_callback_skip_list:
                cmd.multi_cluster_command = True

        # Add base commands to the cluster if they are not already in the cluster
        if base_commands:
            for base_command in base_commands:
                if base_command.name not in self.processed_commands:
                    self.cluster.commands.add(base_command)

        logger.debug(
            f"Processed {len(self.cluster.commands)} commands for cluster {safe_get_attr(self.cluster, 'name')}"
        )

    def _should_process_command(self,
                                command,
                                base_commands: list[Command] = None):
        """Check if command should be processed

        :param command: The command element from the cluster XML file.
        :param base_commands: list[Command]:  (Default value = None)
        :param base_commands: list[Command]:  (Default value = None)
        :returns: True if the command should be processed, False otherwise.

        """
        command_name = command.get("name")
        if command_name in self.processed_commands:
            return False
        self.processed_commands.add(command_name)
        if base_commands:
            base_command = next(
                (cmd for cmd in base_commands if cmd.name == command_name),
                None)
            if not command.get("id") and base_command:
                command.set("id", base_command.id)
        command_id = command.get("id")
        if not check_valid_id(command_id):
            return False

        if not (command_name and command_id):
            logger.debug(
                f"Skipping - missing name or id {command_name} {command_id}")
            return False

        if command_name in [
                safe_get_attr(c, "name") for c in self.processed_commands
        ]:
            logger.debug(
                f"Skipping - command already exists in processed commands {command_name}"
            )
            return False

        if self._check_conformance_restrictions(command, command_name):
            logger.debug(
                f"Skipping - command {command_name} due to conformance restrictions"
            )
            return False

        return True

    def _check_conformance_restrictions(self, command, command_name):
        """Check if the command has any conformance restrictions

        :param command: The command element from the cluster XML file.
        :param command_name: returns: True if the command should be skipped, False otherwise.
        :returns: True if the command should be skipped, False otherwise.

        """
        deprecate_conform = command.find("deprecateConform")
        if deprecate_conform is not None:
            logger.debug(f"Skipping - deprecated command {command_name}")
            return True

        disallow_conform = command.find("disallowConform")
        if disallow_conform is not None:
            logger.debug(f"Skipping - disallow conformance for {command_name}")
            return True

        optional_conform = command.find("optionalConform")
        if optional_conform is not None:
            cond = optional_conform.find("condition")
            if cond is not None and cond.get("name") == "Zigbee":
                logger.debug(
                    f"Skipping - Zigbee specific command {command_name}")
                return True

        return False

    def _create_command(self, command):
        """Create a Command object

        :param command: returns: The created Command object.
        :returns: The created Command object.

        """
        command_name = command.get("name")
        cmd = Command(
            id=command.get("id"),
            name=command_name,
            direction=command.get("direction"),
            response=command.get("response"),
            is_mandatory=command.find("mandatoryConform") is not None,
        )
        if safe_get_attr(self.cluster, "command_handler_available"):
            cmd.command_handler_available = True
        return cmd

    def _process_command_access(self, cmd, command):
        """Process command access

        :param cmd: The command object to process.
        :param command: The command element from the cluster XML file.

        """
        access_elem = command.find("access")
        if access_elem is not None:
            cmd_access = Command.CommandAccess(
                invokePrivilege=access_elem.get("invokePrivilege", None),
                timed=access_elem.get("timed", None),
            )
            cmd.set_access(cmd_access)

    def _process_command_fields(self, cmd, command):
        """Process command fields

        :param cmd: The command object to process.
        :param command: The command element from the cluster XML file.

        """
        for field_elem in command.findall("field"):
            field_id = field_elem.get("id")
            field_name = field_elem.get("name")
            field_type = field_elem.get("type")
            field_default = field_elem.get("default")

            # Check if field should be processed
            if not field_id or not field_name or not field_type:
                continue

            # Process field constraints
            constraint = None
            constraint_elem = field_elem.find("constraint")
            if constraint_elem is not None:
                constraint = {}
                # Handle different constraint types
                for child in constraint_elem:
                    if child.tag == "maxLength":
                        constraint["type"] = "maxLength"
                        constraint["value"] = child.get("value")
                    elif child.tag == "min":
                        constraint["type"] = "min"
                        constraint["value"] = child.get("value")
                    elif child.tag == "max":
                        constraint["type"] = "max"
                        constraint["value"] = child.get("value")
                    elif child.tag == "between":
                        constraint["type"] = "between"
                        from_elem = child.find("from")
                        to_elem = child.find("to")

                        if from_elem is not None and from_elem.get(
                                "value") is not None:
                            constraint["min"] = from_elem.get("value")
                        else:
                            constraint["min"] = "0"

                        if to_elem is not None and to_elem.get(
                                "value") is not None:
                            constraint["max"] = to_elem.get("value")
                        else:
                            constraint["max"] = "0"
                    elif child.tag == "desc":
                        constraint["type"] = "desc"
                        constraint["value"] = None

            field = Command.CommandField(
                id=field_id,
                name=field_name,
                type_=field_type,
                default_value=field_default,
                is_mandatory=field_elem.find("mandatoryConform") is not None,
                constraint=constraint,
            )
            cmd.add_field(field)

    def _process_command_conformance(self, cmd, command):
        """Process command conformance

        :param cmd: The command object to process.
        :param command: The command element from the cluster XML file.

        """
        mandatory_conform = command.find("mandatoryConform")
        optional_conform = command.find("optionalConform")
        otherwise_conform = command.find("otherwiseConform")

        if mandatory_conform is not None:
            cmd.conformance = parse_conformance(mandatory_conform,
                                                self.feature_map)
        elif optional_conform is not None:
            cmd.conformance = parse_conformance(optional_conform,
                                                self.feature_map)
        elif otherwise_conform is not None:
            cmd.conformance = parse_otherwise_conformance(
                otherwise_conform, self.feature_map)
