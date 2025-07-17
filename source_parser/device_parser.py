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
import xml.etree.ElementTree as ET

from source_parser.elements import Cluster
from source_parser.elements import Device
from utils.helper import check_valid_id
from utils.helper import convert_to_snake_case
from utils.helper import esp_name
from utils.helper import safe_get_attr
from utils.logger import setup_logger

logger = setup_logger()


class DeviceParser:
    """ """

    def parse_device_file(self, file_path):
        """Parse a device XML file and return the parsed device object.

        :param file_path: returns: The parsed device object.
        :returns: The parsed device object.

        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            logger.error(f"XML parsing error in {file_path}: {str(e)}")
            return None
        except FileNotFoundError as e:
            logger.error(f"Device XML file not found: {file_path}")
            return None
        except PermissionError as e:
            logger.error(f"Permission denied accessing {file_path}: {str(e)}")
            return None

        device_name, device_id = self._get_name_and_id(root)
        if not check_valid_id(device_id):
            return None
        device_revision = root.get("revision")

        if not self._should_process_device(root):
            return None

        device = Device(id=device_id,
                        name=device_name,
                        revision=device_revision)

        self._parse_revision_history(device, root)
        self._parse_classification(device, root)
        self._parse_conditions(device, root)

        # Parse clusters
        self._parse_clusters(device, root, file_path)

        logger.debug(
            f"****************************Processed device {safe_get_attr(device, 'name')} SUCCESSFULLY****************************"
        )
        return device

    def _parse_choice_groups(self, clusters_element):
        """Parses the choice groups from the clusters element.
        Choice groups are optional conformance rules that specify a minimum number of clusters that must be supported.
        If a choice group is present, the first cluster in the group is marked as mandatory.

        :param clusters_element: The root element of the clusters element.
        :type clusters_element: Element
        :returns: A dictionary of choice groups, where each key is a choice name and the value is a dictionary containing the clusters in the group.
        :rtype: dict

        """
        choice_groups = {}
        for cluster in clusters_element.findall("cluster"):
            optional_conform = cluster.find("optionalConform")
            if optional_conform is not None:
                choice = optional_conform.get("choice")
                if choice:
                    if choice not in choice_groups:
                        choice_groups[choice] = {
                            "clusters": [],
                            "min": int(optional_conform.get("min", "0")),
                            "more": optional_conform.get("more") == "true",
                        }
                    cluster_id = cluster.get("id")
                    cluster_name = cluster.get("name")
                    choice_groups[choice]["clusters"].append(
                        (cluster_id, cluster_name, cluster))
        return choice_groups

    def _parse_clusters(self, device, root, file_path):
        """Parse the clusters from the device XML file.

        :param device: The device object to add the clusters to.
        :param root: The root element of the device XML file.
        :param file_path: The path to the device XML file.

        """
        clusters_element = root.find("clusters")
        if clusters_element is not None:
            feature_name_list = []
            command_name_list = []
            event_name_list = []

            choice_groups = self._parse_choice_groups(clusters_element)

            # Now process each cluster
            for cluster in clusters_element.findall("cluster"):
                cluster_id = cluster.get("id")
                if not check_valid_id(cluster_id):
                    logger.warning(
                        f"Skipping {file_path} as cluster id is not valid: {cluster_id}"
                    )
                    continue
                cluster_name = cluster.get("name")
                cluster_side = cluster.get("side")
                cluster_info = Cluster(name=cluster_name,
                                       id=cluster_id,
                                       revision=0)

                if cluster_side == "server":
                    cluster_info.server_cluster = True
                elif cluster_side == "client":
                    cluster_info.client_cluster = True

                # Check for mandatory conformance
                mandatory_conform = cluster.find("mandatoryConform")
                if (mandatory_conform is not None
                        and mandatory_conform.find("condition") is None
                        and len(mandatory_conform) == 0):
                    cluster_info.is_mandatory = True

                # Parse cluster features
                features = cluster.find("features")
                feature_name_list = []
                if features is not None:
                    for feature in features.findall("feature"):
                        feature_name = feature.get("name")
                        mandatory_conform = feature.find("mandatoryConform")
                        if mandatory_conform is not None:
                            # Only append feature to list if mandatory_conform has no child elements
                            if len(mandatory_conform) == 0:
                                feature_name_list.append(
                                    convert_to_snake_case(feature_name))

                # Parse cluster commands
                command_name_list = []
                commands = cluster.find("commands")
                if commands is not None:
                    for command in commands.findall("command"):
                        command_name = command.get("name")
                        mandatory_conform = command.find("mandatoryConform")
                        if mandatory_conform is not None:
                            # Only append command to list if mandatory_conform has no child elements
                            if len(mandatory_conform) == 0:
                                command_name_list.append(
                                    convert_to_snake_case(command_name))

                cluster_info.feature_name_list = feature_name_list
                cluster_info.command_name_list = command_name_list
                cluster_info.event_name_list = event_name_list
                device.clusters.add(cluster_info)

    def _parse_revision_history(self, device, root):
        """Parse the revision history from the device XML file.

        :param device: The device object to add the revision history to.
        :param root: The root element of the device XML file.

        """
        revision_history_elem = root.find("revisionHistory")
        if revision_history_elem is not None:
            device.revision_history = []
            for revision in revision_history_elem.findall("revision"):
                revision_info = {
                    "revision": revision.get("revision"),
                    "summary": revision.get("summary"),
                }
                device.revision_history.append(revision_info)

    def _parse_classification(self, device, root):
        """Parse the classification from the device XML file.

        :param device: The device object to add the classification to.
        :param root: The root element of the device XML file.

        """
        classification_elem = root.find("classification")
        if classification_elem is not None:
            for attr_name, attr_value in classification_elem.attrib.items():
                device.classification[attr_name] = attr_value

    def _parse_conditions(self, device, root):
        """Parse the conditions from the device XML file.

        :param device: The device object to add the conditions to.
        :param root: The root element of the device XML file.

        """
        conditions_elem = root.find("conditions")
        if conditions_elem is not None:
            device.conditions = []
            for condition in conditions_elem.findall("condition"):
                condition_info = {
                    "name": condition.get("name"),
                    "summary": condition.get("summary"),
                }
                device.conditions.append(condition_info)

    def _should_process_device(self, root):
        """Check if the device should be processed.

        :param root: returns: True if the device should be processed, False otherwise.
        :returns: True if the device should be processed, False otherwise.

        """
        name, id = self._get_name_and_id(root)
        if not name or not id:
            logger.warning(
                f"Device has no name or id, (Either base device type or not supported yet)"
            )
            return False
        return True

    def _get_name_and_id(self, root):
        """Get the name and id of the device.

        :param root: returns: A tuple containing the name and id of the device.
        :returns: A tuple containing the name and id of the device.

        """
        name = root.get("name")
        id = root.get("id")
        return name, id
