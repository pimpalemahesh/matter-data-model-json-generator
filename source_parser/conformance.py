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
from utils.helper import convert_to_snake_case
from utils.helper import safe_get_attr
from utils.logger import setup_logger

logger = setup_logger()


class Conformance:
    """ """

    def __init__(self):
        self.type = None  # mandatory, optional, otherwise, etc.
        self.condition = None  # Nested condition structure
        self.feature_map = {}  # Map of feature codes to feature objects
        # Optional conformance attributes
        # Choice is used to specify the choice conformance condition in optional conformance
        self.choice = None
        self.more = None  # More than min elements required or not True/False
        self.min = None  # Min elements required

    def to_dict(self, attribute_map=None):
        """Convert conformance object to dictionary representation

        :param attribute_map: Dictionary mapping attribute names to their IDs (Default value = None)

        """
        result = {"type": safe_get_attr(self, "type")}
        if safe_get_attr(self, "condition"):
            if attribute_map:
                result[
                    "condition"] = self._replace_attribute_and_command_names(
                        self.condition, attribute_map)
            else:
                result["condition"] = self.condition

        # Add optional conformance attributes if they exist
        if safe_get_attr(self, "choice"):
            result["choice"] = self.choice
        if safe_get_attr(self, "more"):
            result["more"] = self.more
        if safe_get_attr(self, "min"):
            result["min"] = self.min

        return result

    def _replace_attribute_and_command_names(self, condition, attribute_map):
        """Recursively replace attribute and command names with their IDs in the condition

        :param condition: param attribute_map:
        :param attribute_map:

        """
        if isinstance(condition, dict):
            if "attribute" in condition:
                attr_name = condition["attribute"]
                if attr_name in attribute_map:
                    return {"attribute": attribute_map[attr_name]}
                return condition
            elif "command" in condition:
                cmd_name = condition["command"]
                if cmd_name in attribute_map:
                    return {
                        "command": attribute_map[cmd_name][0],
                        "flag": attribute_map[cmd_name][1],
                    }
                return condition
            else:
                return {
                    key:
                    self._replace_attribute_and_command_names(
                        value, attribute_map)
                    for key, value in condition.items()
                }
        elif isinstance(condition, list):
            return [
                self._replace_attribute_and_command_names(item, attribute_map)
                for item in condition
            ]
        return condition

    def has_feature(self, feature_code):
        """Check if conformance involves a specific feature

        :param feature_code:

        """
        if not self.condition:
            return False
        feature_obj = self.feature_map.get(feature_code)
        if not feature_obj:
            return False
        feature_name = feature_obj.func_name
        return _condition_has_feature(self.condition, feature_name)


def _condition_has_feature(condition, feature_code):
    """Recursively check if condition references a specific feature

    :param condition: param feature_code:
    :param feature_code:

    """
    if isinstance(condition, dict):
        # Check for direct feature match
        if "feature" in condition and condition["feature"] == feature_code:
            return True

        for key, value in condition.items():
            if key == "not":
                if (isinstance(value, dict) and "feature" in value
                        and value["feature"] == feature_code):
                    continue
            elif isinstance(value, (dict, list)):
                if _condition_has_feature(value, feature_code):
                    return True

    elif isinstance(condition, list):
        for item in condition:
            if _condition_has_feature(item, feature_code):
                return True
    return False


def parse_conformance(conformance_elem, feature_map):
    """Parse a conformance element from XML

    :param conformance_elem: param feature_map:
    :param feature_map:

    """
    if conformance_elem is None:
        return None
    conformance = Conformance()
    conformance.feature_map = feature_map
    if conformance_elem.tag == "mandatoryConform":
        conformance.type = "mandatory"
    elif conformance_elem.tag == "optionalConform":
        conformance.type = "optional"
        # Extract optional conformance attributes if present
        if conformance_elem.get("choice"):
            conformance.choice = conformance_elem.get("choice")
        if conformance_elem.get("more"):
            # Convert string to boolean for 'more' attribute
            conformance.more = conformance_elem.get("more").lower() == "true"
        if conformance_elem.get("min"):
            # Convert string to integer for 'min' attribute
            try:
                conformance.min = int(conformance_elem.get("min"))
            except (ValueError, TypeError):
                logger.warning(
                    f"Invalid min value in optionalConform: {conformance_elem.get('min')}"
                )
                # Keep as string if conversion fails
                conformance.min = conformance_elem.get("min")
    elif conformance_elem.tag == "deprecateConform":
        conformance.type = "deprecated"
    elif conformance_elem.tag == "disallowConform":
        conformance.type = "disallowed"
    else:
        conformance.type = conformance_elem.tag

    for child in conformance_elem:
        if child.tag.endswith("Term") or child.tag in [
                "attribute",
                "feature",
                "command",
        ]:
            conformance.condition = _parse_condition(child, feature_map)
            break  # We only expect one main condition
    return conformance


def parse_otherwise_conformance(otherwise_elem, feature_map):
    """Parse an 'otherwiseConform' element from XML

    :param otherwise_elem: param feature_map:
    :param feature_map:

    """
    if otherwise_elem is None:
        return None

    conformance = Conformance()
    conformance.type = "otherwise"
    conformance.feature_map = feature_map

    sub_conditions = {}
    for child in otherwise_elem:
        if child.tag in [
                "mandatoryConform",
                "optionalConform",
                "deprecateConform",
                "disallowConform",
        ]:
            child_type = child.tag.replace("Conform", "")
            sub_condition = {}

            # Handle optional conformance attributes for nested optionalConform
            if child.tag == "optionalConform":
                if child.get("choice"):
                    sub_condition["choice"] = child.get("choice")
                if child.get("more"):
                    sub_condition["more"] = child.get("more").lower() == "true"
                if child.get("min"):
                    try:
                        sub_condition["min"] = int(child.get("min"))
                    except (ValueError, TypeError):
                        logger.warning(
                            f"Invalid min value in nested optionalConform: {child.get('min')}"
                        )
                        sub_condition["min"] = child.get("min")

            for subchild in child:
                if subchild.tag.endswith("Term") or subchild.tag in [
                        "attribute",
                        "feature",
                        "command",
                ]:
                    parsed_condition = _parse_condition(subchild, feature_map)
                    if parsed_condition:
                        # Merge the parsed condition with any existing attributes
                        if isinstance(parsed_condition, dict):
                            sub_condition.update(parsed_condition)
                        else:
                            sub_condition["condition"] = parsed_condition
                    break

            # If no condition was parsed but we have attributes, or if we have both condition and attributes
            sub_conditions[
                child_type] = sub_condition if sub_condition else True
    conformance.condition = sub_conditions if sub_conditions else None
    return conformance


def _parse_condition(elem, feature_map):
    """Recursively parse a condition element into a nested dictionary structure

    :param elem: param feature_map:
    :param feature_map:

    """
    if elem is None:
        return None
    if elem.tag == "attribute":
        return {"attribute": elem.get("name")}
    if elem.tag == "command":
        return {"command": elem.get("name")}

    if elem.tag == "feature":
        feature_code = elem.get("name")
        if feature_code in feature_map.keys():
            return {
                "feature":
                convert_to_snake_case(feature_map[feature_code].name)
            }
        else:
            logger.error(f"Feature {feature_code} not found in feature map")
            # Return error code instead of continuing with a conformance object
            return None  # Returning None indicates the feature wasn't found

    condition_type = elem.tag
    if condition_type.endswith("Term"):
        condition_type = condition_type.replace("Term", "")

    if condition_type in ["and", "or"]:
        subconditions = []
        for child in elem:
            subcondition = _parse_condition(child, feature_map)
            if subcondition:
                subconditions.append(subcondition)

        if len(subconditions) > 1:
            return {condition_type: subconditions}
        elif len(subconditions) == 1:
            return {condition_type: subconditions[0]}

    elif condition_type == "not":
        for child in elem:
            subcondition = _parse_condition(child, feature_map)
            if subcondition:
                return {condition_type: subcondition}
    return None
