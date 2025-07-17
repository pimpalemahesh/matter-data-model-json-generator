import argparse
import os
import sys

from core.combine_clusters_devices import combine_clusters_devices
from core.xml_parser import generate_json
from utils.file_utils import create_output_directory
from utils.file_utils import validate_input_paths
from utils.logger import setup_logger

# Add the data_model directory to Python path so we can import from subdirectories
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger = setup_logger()


def get_element_requirements(chip_path,
                             chip_version_dir,
                             output_dir,
                             chip_commit_hash=None):
    """Get the element requirements for the given chip path and chip version.

    :param chip_path:
    :param chip_version_dir:
    :param output_dir:
    :param chip_commit_hash:  (Default value = None)

    """
    generated_output_dir = os.path.join(output_dir, "generated")
    if not create_output_directory(generated_output_dir):
        return

    logger.info(
        f"Generating JSON files for {chip_path} and {chip_version_dir} in {generated_output_dir}"
    )
    generate_json(chip_path, chip_version_dir, generated_output_dir)
    logger.info(f"Generated JSON files in {generated_output_dir}")

    clusters_json_file = os.path.join(generated_output_dir, "clusters.json")
    device_types_json_file = os.path.join(generated_output_dir,
                                          "device_types.json")
    element_requirements_json_file = os.path.join(
        output_dir,
        f"element_requirements_{chip_version_dir}{'_' + chip_commit_hash if chip_commit_hash else ''}.json",
    )
    combine_clusters_devices(clusters_json_file, device_types_json_file,
                             element_requirements_json_file)


def __validate_input_files(chip_path, chip_version_dir, output_dir):
    """Validate the input files for the given chip path and chip version."""
    # Validate that chip_path exists
    if not validate_input_paths(chip_path):
        return False

    # For chip_version_dir, we need to check the full path
    full_chip_version_path = os.path.join(chip_path,
                                          f"data_model/{chip_version_dir}")
    if not validate_input_paths(full_chip_version_path):
        logger.error(
            f"Error: Chip version directory {full_chip_version_path} does not exist"
        )
        return False

    # Create output directory if it doesn't exist
    if not create_output_directory(output_dir):
        return False

    return True


def main():
    """ """
    parser = argparse.ArgumentParser(
        description=
        "Generate JSON files for the given chip path and chip version.")
    parser.add_argument(
        "--chip-path",
        type=str,
        required=True,
        help="Path to the connectedhomeip directory.",
    )
    parser.add_argument(
        "--chip-version-dir",
        type=str,
        required=True,
        help="Chip version directory to process.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        required=False,
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "output"),
        help="Output directory to save the generated JSON files.",
    )
    parser.add_argument(
        "--chip-commit-hash",
        type=str,
        required=False,
        help="Chip commit hash to process.",
    )
    args = parser.parse_args()

    if not __validate_input_files(args.chip_path, args.chip_version_dir,
                                  args.output_dir):
        logger.error("Input validation failed")
        return

    get_element_requirements(args.chip_path, args.chip_version_dir,
                             args.output_dir, args.chip_commit_hash)


if __name__ == "__main__":
    main()
