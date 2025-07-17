#!/usr/bin/env python3
"""
Script to combine clusters.json and device_types.json to create enriched device type definitions.

This script merges the full cluster definitions from clusters.json with the device-specific
cluster information in device_types.json, creating a comprehensive view of each device type
with all cluster attributes, commands, events, and features.
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from utils.file_utils import load_json_file
from utils.file_utils import validate_file_path
from utils.file_utils import write_to_json_file
from utils.helper import esp_name
from utils.logger import setup_logger

# Add parent directory to Python path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = setup_logger()


def create_cluster_lookup(
        clusters: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Create a lookup dictionary for clusters by ID.

    :param clusters: List[Dict[str:
    :param Any]]:

    """
    cluster_lookup = {}
    for cluster in clusters:
        cluster_id = cluster.get("id")
        if cluster_id:
            cluster_lookup[cluster_id] = cluster
    return cluster_lookup


def convert_feature_name_to_code(
        feature_name: str, cluster_features: List[Dict[str, Any]]) -> str:
    """Convert snake_case feature name to feature code.

    :param feature_name: str:
    :param cluster_features: List[Dict[str:
    :param Any]]:

    """
    # Convert snake_case to Title Case for comparison
    target_name = esp_name(feature_name)

    # Find matching feature by name
    for feature in cluster_features:
        if feature.get("name") == target_name or feature.get(
                "code") == target_name:
            return feature.get("code", feature_name)

    # If not found, return original name
    return feature_name


def merge_device_cluster_with_full_definition(
        device_cluster: Dict[str, Any],
        full_cluster: Dict[str, Any]) -> Dict[str, Any]:
    """Merge device-specific cluster info with full cluster definition.

    :param device_cluster: Dict[str:
    :param Any]:
    :param full_cluster: Dict[str:

    """
    merged_cluster = full_cluster.copy()

    # Override with device-specific information
    merged_cluster["type"] = device_cluster.get("type", "server")

    # Handle features - only include features explicitly listed in device_types.json
    device_features = device_cluster.get("features", [])
    full_features = full_cluster.get("features", [])

    # Always filter features based on what's specified in device_types.json
    filtered_features = []

    # Only include features that are explicitly mentioned in device_types.json
    for feature_name in device_features:
        # Convert device feature name to match cluster feature names
        target_name = esp_name(feature_name)

        # Find matching feature in full cluster features
        for feature in full_features:
            feature_name_match = feature.get("name") == target_name
            feature_code_match = feature.get("code") == target_name
            # Also check for direct name match (case-insensitive)
            direct_match = feature.get("name",
                                       "").lower() == feature_name.lower()

            if feature_name_match or feature_code_match or direct_match:
                filtered_features.append(feature)
                break  # Found the feature, move to next device feature

    # Set filtered features (will be empty list if no device features specified)
    merged_cluster["features"] = filtered_features

    # Handle commands - filter based on device_types.json specification
    device_commands = device_cluster.get("commands", [])
    full_commands = full_cluster.get("commands", [])

    # If device has specific commands listed, filter to only those
    if device_commands:
        filtered_commands = []
        for command_name in device_commands:
            # Find matching command in full cluster commands
            for command in full_commands:
                full_command_name = command.get("name", "")
                # Convert command name to snake_case for comparison
                snake_case_name = full_command_name.replace(" ", "_").lower()
                # Also check direct name match
                direct_match = full_command_name.lower() == command_name.lower(
                )

                if snake_case_name == command_name or direct_match:
                    filtered_commands.append(command)
                    break  # Found the command, move to next device command
        merged_cluster["commands"] = filtered_commands
    else:
        # If device has empty commands list, include all commands from cluster
        merged_cluster["commands"] = full_commands

    # Handle attributes - filter based on device_types.json specification
    device_attributes = device_cluster.get("attributes", [])
    full_attributes = full_cluster.get("attributes", [])

    # If device has specific attributes listed, filter to only those
    if device_attributes:
        filtered_attributes = []
        for attribute_name in device_attributes:
            # Find matching attribute in full cluster attributes
            for attribute in full_attributes:
                full_attribute_name = attribute.get("name", "")
                # Convert attribute name to snake_case for comparison
                snake_case_name = full_attribute_name.replace(" ", "_").lower()
                # Also check direct name match
                direct_match = full_attribute_name.lower(
                ) == attribute_name.lower()

                if snake_case_name == attribute_name or direct_match:
                    filtered_attributes.append(attribute)
                    break  # Found the attribute, move to next device attribute
        merged_cluster["attributes"] = filtered_attributes
    else:
        # If device has empty attributes list, include all attributes from cluster
        merged_cluster["attributes"] = full_attributes

    return merged_cluster


def combine_clusters_and_devices(clusters_file: str,
                                 device_types_file: str) -> Dict[str, Any]:
    """Combine clusters.json and device_types.json into enriched device definitions.

    :param clusters_file: str:
    :param device_types_file: str:

    """

    # Load the JSON files
    clusters_data = load_json_file(clusters_file)
    device_types_data = load_json_file(device_types_file)

    if not clusters_data or not device_types_data:
        return {}

    # Create cluster lookup dictionary
    cluster_lookup = create_cluster_lookup(clusters_data)

    # Process each device type
    enriched_devices = []

    for device in device_types_data:
        enriched_device = device.copy()
        enriched_clusters = []

        for device_cluster in device.get("clusters", []):
            cluster_id = device_cluster.get("id")

            if cluster_id in cluster_lookup:
                # Merge device cluster with full cluster definition
                full_cluster = cluster_lookup[cluster_id]
                merged_cluster = merge_device_cluster_with_full_definition(
                    device_cluster, full_cluster)
                enriched_clusters.append(merged_cluster)
            else:
                # If cluster not found in lookup, keep original device cluster
                logger.warning(
                    f"Warning: Cluster {cluster_id} not found in clusters.json"
                )
                enriched_clusters.append(device_cluster)

        enriched_device["clusters"] = enriched_clusters
        enriched_devices.append(enriched_device)

    return enriched_devices


def combine_clusters_devices(clusters_file: str, device_types_file: str,
                             output_file: str):
    """Combine clusters.json and device_types.json to create enriched device definitions.

    :param clusters_file: str:
    :param device_types_file: str:
    :param output_file: str:

    """
    # Combine the data
    enriched_devices = combine_clusters_and_devices(clusters_file,
                                                    device_types_file)

    if not enriched_devices:
        logger.error("Error: Failed to combine data")
        return

    # Write output using centralized function
    if not write_to_json_file(output_file, enriched_devices):
        logger.error(f"Failed to write combined data to {output_file}")
        return

    logger.info(
        f"Successfully wrote enriched device definitions to {output_file}")


def main():
    """ """
    parser = argparse.ArgumentParser(
        description=
        "Combine clusters.json and device_types.json to create enriched device definitions"
    )
    parser.add_argument(
        "--clusters",
        default="generated/clusters.json",
        help="Path to clusters.json file (default: generated/clusters.json)",
    )
    parser.add_argument(
        "--device-types",
        default="generated/device_types.json",
        help=
        "Path to device_types.json file (default: generated/device_types.json)",
    )
    parser.add_argument(
        "--output",
        default="generated/enriched_device_types.json",
        help=
        "Path to output file (default: generated/enriched_device_types.json)",
    )
    parser.add_argument("--pretty",
                        action="store_true",
                        help="Pretty print the output JSON")

    args = parser.parse_args()
    clusters_json_file = args.clusters
    device_types_json_file = args.device_types
    enriched_device_types_json_file = args.output

    # Check if input files exist using centralized validation
    if not validate_file_path(clusters_json_file):
        logger.error(
            f"Error: Clusters file {clusters_json_file} does not exist")
        return

    if not validate_file_path(device_types_json_file):
        logger.error(
            f"Error: Device types file {device_types_json_file} does not exist"
        )
        return

    logger.info(f"Loading clusters from: {clusters_json_file}")
    logger.info(f"Loading device types from: {device_types_json_file}")

    combine_clusters_devices(clusters_json_file, device_types_json_file,
                             enriched_device_types_json_file)


if __name__ == "__main__":
    main()
