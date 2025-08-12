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
import argparse
import os
import sys
import xml.etree.ElementTree as ET

from source_parser.cluster_parser import ClusterParser
from source_parser.device_parser import DeviceParser
from utils.file_utils import create_output_directory
from utils.file_utils import get_file_list_by_extension
from utils.file_utils import list_directory
from utils.file_utils import validate_directory_path
from utils.file_utils import write_to_json_file
from utils.logger import setup_logger

# Add parent directory to path so we can import from parent modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Also add the data_model directory itself for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = setup_logger()


def get_base_and_derived_cluster_files(input_dir):
    """Get all base and derived cluster files from the input directory.

    :param input_dir: returns: A list of base and derived cluster files.
    :returns: A list of base and derived cluster files.

    """
    base_cluster_files = []
    derived_cluster_files = []

    file_list = list_directory(input_dir)
    if file_list is None:
        return [], []

    for file_name in file_list:
        if file_name.endswith(".xml"):
            file_path = os.path.join(input_dir, file_name)
            try:
                tree = ET.parse(file_path)
                root = tree.getroot()
                classification = root.find("classification")
                if classification is not None and classification.get(
                        "hierarchy") == "derived":
                    derived_cluster_files.append(file_path)
                else:
                    base_cluster_files.append(file_path)
            except ET.ParseError as e:
                logger.error(f"XML parsing error in {file_path}: {str(e)}")
                continue
            except FileNotFoundError:
                logger.error(f"Cluster file not found: {file_path}")
                continue
            except PermissionError:
                logger.error(
                    f"Permission denied accessing cluster file: {file_path}")
                continue
        else:
            logger.error(f"Skipping {file_name} as it is not a valid file")
            continue
    return base_cluster_files, derived_cluster_files


def process_cluster_files(
    input_dir,
    cluster_json_file,
    yaml_file_path,
):
    """Process all cluster XML files from input directory and generate intermediate cluster json file.
    This function is used to process all cluster XML files from input directory and generate intermediate cluster json file.
    First it generates base cluster objects as during parsing of the derived cluster files, the base cluster objects are needed.
    Then it generates derived cluster objects.

    :param input_dir: Path to the directory containing the cluster XML files.
    :param cluster_json_file: Path to the file where the cluster JSON will be written.
    :param yaml_file_path: Path to the YAML file containing the configuration data.
    :returns: None

    """
    # Stores list of base and derived cluster XML files to be processed
    base_cluster_xml_files, derived_cluster_xml_files = get_base_and_derived_cluster_files(
        input_dir)
    if len(base_cluster_xml_files) == 0 and len(
            derived_cluster_xml_files) == 0:
        logger.error(f"No cluster XML files found in {input_dir}")
        return

    cluster_parser = ClusterParser()
    # Stores list of base and derived cluster objects
    base_clusters = []
    derived_clusters = []

    # Process base cluster files
    for file_path in base_cluster_xml_files:
        cluster_list = cluster_parser.parse_cluster_file(
            file_path=file_path,
            yaml_file_path=yaml_file_path,
        )

        if cluster_list is None or len(cluster_list) == 0:
            logger.error(
                f"********************** Processing of {os.path.basename(file_path)} failed************************"
            )
            continue

        base_clusters.extend(cluster_list)
        logger.info(
            f"********************** Processing of {os.path.basename(file_path)} completed************************"
        )

    # Process derived cluster files
    for file_path in derived_cluster_xml_files:
        cluster_list = cluster_parser.parse_cluster_file(
            file_path=file_path,
            yaml_file_path=yaml_file_path,
            base_clusters=base_clusters,
        )

        if cluster_list is None or len(cluster_list) == 0:
            logger.error(
                f"********************** Processing of {os.path.basename(file_path)} failed************************"
            )
            continue

        derived_clusters.extend(cluster_list)
        logger.info(
            f"********************** Processing of {os.path.basename(file_path)} completed************************"
        )

    clusters = base_clusters + derived_clusters
    # Convert clusters to list of dictionaries
    clusters_list = [cluster.to_dict() for cluster in clusters]
    clusters_list.sort(key=lambda x: int(x.get("id"), 16))

    if not write_to_json_file(cluster_json_file, clusters_list):
        logger.error(f"Failed to write to {cluster_json_file}")
        return

    logger.info(
        f"\n\n--------------------------------------------------PROCESSING COMPLETE | GENERATED cluster json in {cluster_json_file}--------------------------------------------------\n\n"
    )


def parse_single_device_file(device_parser, file_path):
    """Parse a single device XML file and return the parsed device object.

    :param device_parser: Instance of DeviceParser.
    :param file_path: returns: Device object
    :returns: Device object

    """
    return device_parser.parse_device_file(file_path)


def parse_single_cluster_file(cluster_parser, file_path, yaml_file_path):
    """Parse a single cluster XML file and return the parsed cluster object.

    :param cluster_parser: Instance of ClusterParser.
    :param file_path: Path to the cluster XML file.
    :param yaml_file_path: returns: Cluster object
    :returns: Cluster object

    """
    return cluster_parser.parse_cluster_file(file_path, yaml_file_path)


def process_device_files(input_dir, device_json_file):
    """Process all device XML files from input directory and generate intermediate device json file.

    :param input_dir: Path to the directory containing the device XML files.
    :param device_json_file: returns: None
    :returns: None

    """
    file_list = list_directory(input_dir)
    if file_list is None:
        return

    devices = []
    device_parser = DeviceParser()
    for file_name in file_list:
        if file_name.endswith(".xml"):
            file_path = os.path.join(input_dir, file_name)
            device = parse_single_device_file(device_parser=device_parser,
                                              file_path=file_path)
            if device is None or device.name is None:
                logger.error(
                    f"********************** Processing of {file_name} failed************************"
                )
                continue

            devices.append(device)
            logger.info(
                f"********************** Processing of {file_name} completed************************"
            )
        else:
            logger.error(f"Skipping {file_name} as it is not a valid file")
            continue

    devices_list = [device.to_dict() for device in devices]
    devices_list.sort(key=lambda x: int(x.get("id"), 16))
    # Save devices to JSON
    if not write_to_json_file(device_json_file, devices_list):
        logger.error(f"Failed to write to {device_json_file}")
        return
    logger.info(
        f"\n\n--------------------------------------------------PROCESSING COMPLETE | GENERATED device json in {device_json_file}--------------------------------------------------\n\n"
    )


def generate_json(chip_path, chip_version_dir, output_dir):
    """Generate JSON files for the given chip path and chip version.

    :param chip_path: param chip_version_dir:
    :param output_dir:
    :param chip_version_dir:

    """

    assert chip_path is not None, "Chip path is not provided"

    # Yaml file contains list of clusters supporting specific functions e.g. Shutdown callback functions, pre attribute change callback functions, etc.
    yaml_file_path = os.path.join(chip_path,
                                  "src/app/common/templates/config-data.yaml")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    json_generated_dir = os.path.join(current_dir, output_dir)
    if not create_output_directory(json_generated_dir):
        return

    # Intermediate json files.
    # Cluster files contains all the clusters with their attributes, commands, events, etc.
    # Device files contains all the device types with the clusters used by the device.
    cluster_json_file = os.path.join(json_generated_dir, "clusters.json")
    device_json_file = os.path.join(json_generated_dir, "device_types.json")

    # Process all files from default directories
    xml_input_dir = os.path.join(chip_path, f"data_model/{chip_version_dir}/")
    cluster_input_dir = os.path.join(xml_input_dir, "clusters/")
    device_input_dir = os.path.join(xml_input_dir, "device_types/")

    logger.info(
        "************************************************* Processing device files *************************************************"
    )
    # Process device files
    process_device_files(input_dir=device_input_dir,
                         device_json_file=device_json_file)

    logger.info(
        "\n\n************************************************* Processing cluster files *************************************************"
    )
    # Process cluster files
    if yaml_file_path is None:
        logger.error("Yaml file path is not provided")
        return
    process_cluster_files(
        input_dir=cluster_input_dir,
        yaml_file_path=yaml_file_path,
        cluster_json_file=cluster_json_file,
    )


# Main execution
def main():
    """ """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description=
        "Process cluster XML files and generate C++ and header files.")
    parser.add_argument(
        "--chip_path",
        type=str,
        required=True,
        help="Path to the connectedhomeip directory.",
    )
    parser.add_argument(
        "--chip_version_dir",
        choices=["1.3", "1.4", "1.4.1", "master"],
        required=True,
        help=
        "XML files directory version to process. Supported versions are 1.3, 1.4, 1.4.1, master.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=False,
        default="output",
        help="Output directory to save the generated JSON files.",
    )

    args = parser.parse_args()
    chip_path = args.chip_path
    chip_version_dir = args.chip_version_dir
    output_dir = args.output_dir

    generate_json(chip_path, chip_version_dir, output_dir)


if __name__ == "__main__":
    main()
