#!/usr/bin/env python3
"""
Basic functionality tests for Matter Data Model JSON Generator.

This module contains basic tests to verify core functionality and
serve as examples for writing additional tests.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

from utils.file_utils import create_output_directory
from utils.file_utils import validate_directory_path
from utils.file_utils import validate_file_path
from utils.helper import check_valid_id
from utils.helper import convert_to_snake_case
from utils.helper import esp_name
from utils.logger import setup_logger

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestFileUtils(unittest.TestCase):
    """Test file utility functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_output_directory(self):
        """Test directory creation utility."""
        test_dir = os.path.join(self.temp_dir, "test_output")

        # Test creating new directory
        result = create_output_directory(test_dir)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(test_dir))

        # Test existing directory
        result = create_output_directory(test_dir)
        self.assertTrue(result)

    def test_validate_directory_path(self):
        """Test directory path validation."""
        # Test existing directory
        self.assertTrue(validate_directory_path(self.temp_dir))

        # Test non-existing directory
        non_existing = os.path.join(self.temp_dir, "non_existing")
        self.assertFalse(validate_directory_path(non_existing))

    def test_validate_file_path(self):
        """Test file path validation."""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        # Test existing file
        self.assertTrue(validate_file_path(test_file))

        # Test non-existing file
        non_existing = os.path.join(self.temp_dir, "non_existing.txt")
        self.assertFalse(validate_file_path(non_existing))


class TestHelperFunctions(unittest.TestCase):
    """Test helper utility functions."""

    def test_esp_name(self):
        """Test ESP naming convention conversion."""
        test_cases = [
            ("OnOff Cluster", "OnOffCluster"),
            ("Level Control", "LevelControl"),
            ("Temperature Measurement", "TemperatureMeasurement"),
            ("Simple Name", "SimpleName"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input=input_name):
                result = esp_name(input_name)
                self.assertEqual(result, expected)

    def test_convert_to_snake_case(self):
        """Test snake case conversion."""
        test_cases = [
            ("OnOffCluster", "on_off_cluster"),
            ("LevelControl", "level_control"),
            ("TemperatureMeasurement", "temperature_measurement"),
            ("SimpleWord", "simple_word"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input=input_name):
                result = convert_to_snake_case(input_name)
                self.assertEqual(result, expected)

    def test_check_valid_id(self):
        """Test ID validation."""
        valid_ids = ["0x0006", "0x0008", "0x001D", "0xFFFF"]
        invalid_ids = [None, "", "invalid", "0x", "not_hex"]

        for valid_id in valid_ids:
            with self.subTest(id=valid_id):
                self.assertTrue(check_valid_id(valid_id))

        for invalid_id in invalid_ids:
            with self.subTest(id=invalid_id):
                self.assertFalse(check_valid_id(invalid_id))


class TestLogging(unittest.TestCase):
    """Test logging functionality."""

    def test_setup_logger(self):
        """Test logger setup."""
        logger = setup_logger()
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "matter_json_generator")


class TestIntegration(unittest.TestCase):
    """Integration tests for core functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skip("Requires actual connectedhomeip repository")
    def test_basic_parsing_workflow(self):
        """Test basic parsing workflow (requires real data)."""
        # This test would need actual connectedhomeip data
        # It's skipped by default but serves as an example
        from core.xml_parser import generate_json

        chip_path = "/path/to/connectedhomeip"  # Would need real path
        chip_version = "1.4"
        output_dir = os.path.join(self.temp_dir, "test_output")

        # This would test the actual parsing
        # generate_json(chip_path, chip_version, output_dir)
        pass


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
