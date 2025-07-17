import json
import os
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from utils.logger import setup_logger

logger = setup_logger()

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning(
        "PyYAML not available. YAML file operations will be disabled.")


def create_dir(dir_path: str) -> bool:
    """Create a directory if it does not exist

    :param dir_path: str:

    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except PermissionError:
        logger.error(f"Permission denied creating directory: {dir_path}")
        return False
    except OSError as e:
        logger.error(f"OS error creating directory {dir_path}: {str(e)}")
        return False


def validate_file_path(file_path: str) -> bool:
    """Validate a file path

    :param file_path: str:

    """
    try:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return False
        return True
    except PermissionError:
        logger.error(f"Permission denied accessing file: {file_path}")
        return False
    except OSError as e:
        logger.error(f"OS error accessing file {file_path}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error accessing file {file_path}: {str(e)}")
        return False


def validate_directory_path(dir_path: str) -> bool:
    """Validate a directory path

    :param dir_path: str:

    """
    try:
        if not os.path.exists(dir_path):
            logger.error(f"Directory not found: {dir_path}")
            return False
        if not os.path.isdir(dir_path):
            logger.error(f"Path is not a directory: {dir_path}")
            return False
        return True
    except PermissionError:
        logger.error(f"Permission denied accessing directory: {dir_path}")
        return False
    except OSError as e:
        logger.error(f"OS error accessing directory {dir_path}: {str(e)}")
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error accessing directory {dir_path}: {str(e)}")
        return False


def list_directory(dir_path: str) -> Optional[List[str]]:
    """List directory contents with error handling

    :param dir_path: str:

    """
    try:
        return os.listdir(dir_path)
    except FileNotFoundError:
        logger.error(f"Directory not found: {dir_path}")
        return None
    except PermissionError:
        logger.error(f"Permission denied accessing directory: {dir_path}")
        return None
    except OSError as e:
        logger.error(f"OS error accessing directory {dir_path}: {str(e)}")
        return None


def load_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load and parse a JSON file with error handling

    :param file_path: str:

    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"JSON file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file {file_path}: {str(e)}")
        return None
    except PermissionError:
        logger.error(f"Permission denied reading file: {file_path}")
        return None
    except OSError as e:
        logger.error(f"OS error reading file {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error reading JSON file {file_path}: {str(e)}")
        return None


def write_to_json_file(file_path: str, data: Any) -> bool:
    """Write data to a JSON file

    :param file_path: Path to the file where the data will be written.
    :param data: Data to be written to the JSON file
    :param file_path: str:
    :param data: Any:
    :returns: True if successful, False otherwise

    """
    try:
        # Create parent directories if they don't exist
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not create_dir(parent_dir):
            return False

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except FileNotFoundError as e:
        logger.error(f"Directory not found for file {file_path}: {str(e)}")
        return False
    except PermissionError as e:
        logger.error(f"Permission denied writing to {file_path}: {str(e)}")
        return False
    except OSError as e:
        logger.error(f"OS error writing to {file_path}: {str(e)}")
        return False
    except TypeError as e:
        logger.error(f"Invalid data type for JSON serialization: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error writing to {file_path}: {str(e)}")
        return False


def create_output_directory(output_dir: str) -> bool:
    """Create output directory and ensure it's writable

    :param output_dir: str:

    """
    if not create_dir(output_dir):
        return False

    # Test if directory is writable
    test_file = os.path.join(output_dir, ".test_write")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return True
    except (PermissionError, OSError) as e:
        logger.error(
            f"Output directory {output_dir} is not writable: {str(e)}")
        return False


def get_file_list_by_extension(dir_path: str, extension: str) -> List[str]:
    """Get list of files with specific extension from directory

    :param dir_path: str:
    :param extension: str:

    """
    file_list = list_directory(dir_path)
    if file_list is None:
        return []

    return [
        os.path.join(dir_path, file_name) for file_name in file_list
        if file_name.endswith(extension)
    ]


def validate_input_paths(*paths: str) -> bool:
    """Validate multiple input paths (files or directories)

    :param *paths: str:

    """
    for path in paths:
        if not os.path.exists(path):
            logger.error(f"Path does not exist: {path}")
            return False
    return True


def safe_file_operation(operation_name: str, operation_func, *args, **kwargs):
    """Safely execute a file operation with error handling

    :param operation_name: str:
    :param operation_func:
    :param *args:
    :param **kwargs:

    """
    try:
        return operation_func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Error during {operation_name}: {str(e)}")
        return None


def load_yaml_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load and parse a YAML file with error handling

    :param file_path: str:

    """
    if not YAML_AVAILABLE:
        logger.error("PyYAML is not installed. Cannot load YAML files.")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"YAML file not found: {file_path}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file {file_path}: {str(e)}")
        return None
    except PermissionError:
        logger.error(f"Permission denied reading file: {file_path}")
        return None
    except OSError as e:
        logger.error(f"OS error reading file {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error reading YAML file {file_path}: {str(e)}")
        return None


def load_text_file(file_path: str) -> Optional[str]:
    """Load a text file with error handling

    :param file_path: str:

    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Text file not found: {file_path}")
        return None
    except PermissionError:
        logger.error(f"Permission denied reading file: {file_path}")
        return None
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading file {file_path}: {str(e)}")
        return None
    except OSError as e:
        logger.error(f"OS error reading file {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error reading text file {file_path}: {str(e)}")
        return None
