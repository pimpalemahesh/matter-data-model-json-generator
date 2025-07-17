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
import yaml

enums_not_used_as_type_in_xml = []
command_interface_only_clusters = []
clusters_with_init_functions = []
clusters_with_attribute_changed_functions = []
clusters_with_shutdown_functions = []
clusters_with_pre_attribute_change_functions = []


class ConfigData:
    """ """

    config_data = None

    def __init__(self, file_path):
        self.load_config_data(file_path)
        self.enums_not_used_as_type_in_xml = self.config_data.get(
            "EnumsNotUsedAsTypeInXml", [])
        self.command_interface_only_clusters = self.config_data.get(
            "CommandInterfaceOnlyClusters", [])
        self.clusters_with_init_functions = self.config_data.get(
            "ClustersWithInitFunctions", [])
        self.clusters_with_attribute_changed_functions = self.config_data.get(
            "ClustersWithAttributeChangedFunctions", [])
        self.clusters_with_shutdown_functions = self.config_data.get(
            "ClustersWithShutdownFunctions", [])
        self.clusters_with_pre_attribute_change_functions = self.config_data.get(
            "ClustersWithPreAttributeChangeFunctions", [])

    def load_config_data(self, file_path):
        """

        :param file_path:

        """
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
