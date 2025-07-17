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
from source_parser.conformance import parse_conformance
from source_parser.conformance import parse_otherwise_conformance
from source_parser.elements import Feature
from utils.helper import safe_get_attr
from utils.logger import setup_logger
from utils.mapping import cpp_reserved_words

logger = setup_logger()


class FeatureParser:
    """ """

    def __init__(self, root, cluster):
        self.root = root
        self.cluster = cluster
        self.feature_map = {}
        self.processed_features = set()

    def create_feature_map(self):
        """Create a map of features from XML. e.g. {"LT": <lighting_feature_obj>}

        :param root: The root element of the cluster XML file.
        :returns: A map of features.

        """
        features_elem = self.root.find("features")
        if features_elem is None:
            logger.debug(f"No features found for cluster {self.cluster.name}")
            return self.feature_map

        feature_codes = self._collect_features()

        # create basic features without conformance
        for feature_elem in features_elem.findall("feature"):
            feature = self._create_basic_feature(feature_elem, feature_codes)
            if feature:
                self.feature_map[feature.code] = feature

        # parse conformance now that all features exist in the map
        features_to_remove = []
        for feature_elem in features_elem.findall("feature"):
            feature_code = feature_elem.get("code")
            if feature_code in self.feature_map:
                should_remove = self._parse_feature_conformance(
                    feature_elem, self.feature_map[feature_code])
                if should_remove:
                    features_to_remove.append(feature_code)

        # remove features with disallowed conformance
        for feature_code in features_to_remove:
            del self.feature_map[feature_code]

        return self.feature_map

    def _collect_features(self) -> list[str]:
        """Collect features from XML. e.g. ["LT", "AC"]


        :returns: A list of features.

        """
        features_elem = self.root.find("features")
        if features_elem is None:
            return []
        features = []
        for feature_elem in features_elem.findall("feature"):
            features.append(feature_elem.get("code"))
        return features

    def _create_basic_feature(self, feature_elem, feature_codes: list[str]):
        """Create a basic Feature object from XML element without conformance

        :param feature_elem: param feature_codes: A list of all feature codes in the cluster.
        :param feature_codes: list[str]:
        :returns: The created Feature object.

        """
        feature_name = feature_elem.get("name")
        if feature_name in self.processed_features:
            return None
        self.processed_features.add(feature_name)
        feature_code = feature_elem.get("code")
        feature_summary = feature_elem.get("summary")
        feature_bit = feature_elem.get("bit")
        if not (feature_name and feature_code):
            logger.warning(
                f"Skipping feature due to missing required attributes feature_name: {feature_name} feature_code: {feature_code}"
            )
            return None

        feature_obj = Feature(
            name=(feature_name if feature_name.lower()
                  not in cpp_reserved_words else self.cluster.esp_name + "_" +
                  feature_name),
            code=feature_code,
            id=self._compute_feature_id(int(feature_bit)),
        )

        # Add summary if available
        if feature_summary:
            feature_obj.summary = feature_summary

        return feature_obj

    def _parse_feature_conformance(self, feature_elem, feature_obj):
        """Parse and set conformance for a feature object

        :param feature_elem: XML element containing conformance information
        :param feature_obj: The Feature object to set conformance on
        :returns: True if feature should be removed (disallowed), False otherwise

        """
        # Parse feature conformance if available
        optional_conform = feature_elem.find("optionalConform")
        mandatory_conform = feature_elem.find("mandatoryConform")
        disallowed_conform = feature_elem.find("disallowedConform")
        otherwise_conform = feature_elem.find("otherwiseConform")

        if mandatory_conform is not None:
            feature_obj.conformance = parse_conformance(
                mandatory_conform, self.feature_map)
        elif optional_conform is not None:
            feature_obj.conformance = parse_conformance(
                optional_conform, self.feature_map)
        elif disallowed_conform is not None:
            # Feature with disallowed conformance should be removed
            return True
        elif otherwise_conform is not None:
            feature_obj.conformance = parse_otherwise_conformance(
                otherwise_conform, self.feature_map)

        return False

    def _compute_feature_id(self, feature_bit):
        """Compute the feature id based on the number of existing features. e.g. feature_bit = 0x1, feature_id = 0x1 << 0x1 = 0x2, feature_bit = 0x2, feature_id = 0x1 << 0x2 = 0x4 etc.

        :param feature_bit: returns: The computed feature id.
        :returns: The computed feature id.

        """
        feature_id = 0x1 << feature_bit
        return feature_id

    def compute_features(self,
                         feature_map,
                         base_features: list[Feature] = None):
        """Add feature data to cluster

        :param feature_map: The feature map.
        :param base_features: list[Feature]:  (Default value = None)
        :param base_features: list[Feature]:  (Default value = None)
        :returns: None

        """
        for feature_obj in feature_map.values():
            self._process_feature(feature_obj, base_features)
            self.cluster.features.add(feature_obj)

        # Add base features to the cluster if they are not already in the cluster
        if base_features:
            for base_feature in base_features:
                if base_feature.code not in self.feature_map.keys():
                    self.cluster.features.add(base_feature)

    def _process_feature(self,
                         feature_obj,
                         base_features: list[Feature] = None):
        """This will create a list of attributes, commands and events those having conformance with the given feature.

        :param feature_obj: The feature object to process.
        :param base_features: list[Feature]:  (Default value = None)
        :param base_features: list[Feature]:  (Default value = None)
        :returns: None

        """
        # Match attributes to features
        feature_attribute_list = self._match_attribute_features(
            feature_obj.code, self.cluster.get_attribute_list())
        if feature_attribute_list:
            feature_obj.add_attribute_list(feature_attribute_list)

        # Match commands to features
        feature_command_list = self._match_command_features(
            feature_obj.code, self.cluster.get_command_list())

        if feature_command_list:
            feature_obj.add_command_list(feature_command_list)

        # Match events to features
        feature_event_list = self._match_event_features(
            feature_obj.code, self.cluster.get_event_list())
        if feature_event_list:
            feature_obj.add_event_list(feature_event_list)

    def _match_attribute_features(self, feature_code, attribute_list):
        """Get list of attributes matched with current feature

        :param feature_code: The code of the feature.
        :param attribute_list: returns: A list of attributes that have conformance with the given feature.
        :returns: A list of attributes that have conformance with the given feature.

        """
        return {
            attr
            for attr in attribute_list if safe_get_attr(attr, "conformance")
            and safe_get_attr(attr, "conformance").has_feature(feature_code)
        }

    def _match_command_features(self, feature_code, command_list):
        """Get list of commands matched with current feature

        :param feature_code: The code of the feature.
        :param command_list: returns: A list of commands that have conformance with the given feature.
        :returns: A list of commands that have conformance with the given feature.

        """
        return {
            cmd
            for cmd in command_list if safe_get_attr(cmd, "conformance")
            and safe_get_attr(cmd, "conformance").has_feature(feature_code)
        }

    def _match_event_features(self, feature_code, event_list):
        """Get list of events matched with current feature

        :param feature_code: The code of the feature.
        :param event_list: returns: A list of events that have conformance with the given feature.
        :returns: A list of events that have conformance with the given feature.

        """
        return {
            evt
            for evt in event_list if safe_get_attr(evt, "conformance")
            and safe_get_attr(evt, "conformance").has_feature(feature_code)
        }
