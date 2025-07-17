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
from abc import abstractmethod

from utils.helper import chip_name
from utils.helper import convert_to_snake_case
from utils.helper import esp_name
from utils.mapping import *


def get_id_name_lambda():
    """ """
    return lambda x: (int(x.get_id(), 16), x.name)


def modify_id(id):
    """

    :param id:

    """
    if isinstance(id, str):
        id_int = int(id, 16) if id.startswith("0x") else int(id)
    else:
        id_int = int(id)
    return f"0x{id_int:04X}"


class BaseElement:
    """ """

    def __init__(self, name, id):
        assert name, "Name is required"
        self.name = convert_to_snake_case(name)
        self.id = modify_id(id)
        self.esp_name = esp_name(name)
        self.chip_name = chip_name(name)
        self.func_name = convert_to_snake_case(name)

    def get_id(self):
        """ """
        return self.id


class BaseClusterElement(BaseElement):
    """ """

    def __init__(self, name, id, is_mandatory):
        if name and name in cpp_reserved_words or name.lower(
        ) in cpp_reserved_words:
            name = name + "_Cluster"
        if name in cluster_name_mapping:
            name = cluster_name_mapping[name]
        super().__init__(name=name, id=id)
        self.is_mandatory = is_mandatory


class BaseCluster(BaseClusterElement):
    """ """

    def __init__(self, name, id, revision, is_mandatory):
        super().__init__(name=name, id=id, is_mandatory=is_mandatory)
        self.revision = revision
        self.server_cluster = False
        self.client_cluster = False
        self.command_handler_available = False
        self.init_function_available = False
        self.attribute_changed_function_available = False
        self.shutdown_function_available = False
        self.pre_attribute_change_function_available = False
        self.delegate_init_callback_available = False
        self.plugin_init_cb_available = False

        self.delegate_init_callback = None
        self.plugin_server_init_callback = None
        self.role = None

    def get_revision(self):
        """ """
        return self.revision

    @abstractmethod
    def get_attributes(self):
        """ """
        pass

    @abstractmethod
    def get_commands(self):
        """ """
        pass

    @abstractmethod
    def get_events(self):
        """ """
        pass

    @abstractmethod
    def get_features(self):
        """ """
        pass


class BaseAttribute(BaseClusterElement):
    """ """

    def __init__(self, name, id, type_, is_mandatory, default_value):
        if name and name in cpp_reserved_words or name.lower(
        ) in cpp_reserved_words:
            name = name + "_Attribute"
        super().__init__(name=name, id=id, is_mandatory=is_mandatory)
        self.type = type_
        self.default_value = default_value
        self.is_nullable = False


class BaseCommand(BaseClusterElement):
    """ """

    def __init__(self, name, id, is_mandatory, direction, response):
        if name and name in cpp_reserved_words or name.lower(
        ) in cpp_reserved_words:
            name = name + "_Command"
        super().__init__(name=name, id=id, is_mandatory=is_mandatory)
        self.direction = direction
        self.response = response


class BaseEvent(BaseClusterElement):
    """ """

    def __init__(self, name, id, is_mandatory):
        if name and name in cpp_reserved_words or name.lower(
        ) in cpp_reserved_words:
            name = name + "_Event"
        super().__init__(name=name, id=id, is_mandatory=is_mandatory)


class BaseFeature(BaseClusterElement):
    """ """

    def __init__(self, name, id, is_mandatory):
        if name and name in cpp_reserved_words or name.lower(
        ) in cpp_reserved_words:
            name = name + "_Feature"
        super().__init__(name=name, id=id, is_mandatory=is_mandatory)

    @abstractmethod
    def get_attributes(self):
        """ """
        pass

    @abstractmethod
    def get_commands(self):
        """ """
        pass

    @abstractmethod
    def get_events(self):
        """ """
        pass


class BaseDevice(BaseElement):
    """ """

    def __init__(self, name, id, revision):
        super().__init__(name=name, id=id)
        self.filename = self.esp_name + "_device"
        self.revision = revision

    def get_device_type_id(self):
        """ """
        return self.id

    def get_device_type_version(self):
        """ """
        return self.revision

    @abstractmethod
    def get_clusters(self):
        """ """
        pass

    @abstractmethod
    def get_mandatory_clusters(self):
        """ """
        pass
