# Matter Data Model JSON Generator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

A powerful Python tool that parses XML data model files from the Matter (formerly Connected Home over IP) specification and generates structured JSON representations for clusters, device types, and their relationships.

## 🚀 Features

- **XML to JSON Conversion**: Parse Matter XML data model files and convert them to structured JSON format
- **Multi-Version Support**: Compatible with Matter specification versions 1.3, 1.4, 1.4.1, and master
- **Comprehensive Parsing**: Extracts clusters, device types, attributes, commands, events, and features
- **Device Type Enrichment**: Combines cluster definitions with device-specific information
- **Conformance Analysis**: Handles complex conformance conditions and feature dependencies
- **Production Ready**: Robust error handling, logging, and validation

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Output Format](#output-format)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Access to the Matter (connectedhomeip) repository

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install from Source

```bash
git clone https://github.com/pimpalemahesh/matter-data-model-json-generator.git
cd matter-data-model-json-generator
pip install -e .
```

## ⚡ Quick Start

```bash
python app.py \
  --chip-path /path/to/connectedhomeip \
  --chip-version-dir 1.4 \
  --output-dir ./output
```

This will generate:

- `output/generated/clusters.json` - All cluster definitions
- `output/generated/device_types.json` - All device type definitions
- `output/element_requirements_1.4.json` - Enriched device definitions

## 📖 Usage

### Command Line Interface

```bash
python app.py [OPTIONS]
```

#### Required Arguments

- `--chip-path`: Path to the connectedhomeip directory
- `--chip-version-dir`: Matter version to process (`1.3`, `1.4`, `1.4.1`, `master`)

#### Optional Arguments

- `--output-dir`: Output directory (default: `./output`)
- `--chip-commit-hash`: Specific commit hash for versioning

### Python API

```python
from core.xml_parser import generate_json
from core.combine_clusters_devices import combine_clusters_devices

# Generate base JSON files
generate_json(
    chip_path="/path/to/connectedhomeip",
    chip_version_dir="1.4",
    output_dir="./output/generated"
)

# Combine and enrich data
combine_clusters_devices(
    clusters_file="./output/generated/clusters.json",
    device_types_file="./output/generated/device_types.json",
    output_file="./output/enriched_devices.json"
)
```

## 🔧 API Reference

### Core Functions

#### `generate_json(chip_path, chip_version_dir, output_dir)`

Parses XML files and generates JSON representations.

**Parameters:**

- `chip_path` (str): Path to connectedhomeip repository
- `chip_version_dir` (str): Version directory to process
- `output_dir` (str): Directory for output files

#### `combine_clusters_devices(clusters_file, device_types_file, output_file)`

Combines cluster and device type data into enriched definitions.

**Parameters:**

- `clusters_file` (str): Path to clusters.json
- `device_types_file` (str): Path to device_types.json
- `output_file` (str): Path for output file

### Parsers

- **ClusterParser**: Parses cluster XML files
- **DeviceParser**: Parses device type XML files
- **AttributeParser**: Extracts attribute definitions
- **CommandParser**: Extracts command definitions
- **EventParser**: Extracts event definitions
- **FeatureParser**: Extracts feature definitions

## 📄 Output Format

### Clusters JSON

```json
{
  "name": "OnOff",
  "id": "0x0006",
  "revision": "1",
  "attributes": [
    {
      "name": "OnOff",
      "id": "0x0000"
    }
  ],
  "commands": [
    {
      "name": "Off",
      "id": "0x00"
    }
  ],
  "events": [],
  "features": []
}
```

### Device Types JSON

```json
{
  "name": "Dimmable Light",
  "id": "0x0101",
  "revision": "1",
  "clusters": [
    {
      "name": "OnOff",
      "id": "0x0006",
      "type": "server",
      "features": [],
      "commands": [],
      "attributes": []
    }
  ]
}
```

## 📚 Examples

### Example 1: Parse Specific Version

```bash
python app.py \
  --chip-path ~/connectedhomeip \
  --chip-version-dir 1.4 \
  --output-dir ./matter-1.4-data
```

### Example 2: Include Commit Hash

```bash
python app.py \
  --chip-path ~/connectedhomeip \
  --chip-version-dir master \
  --chip-commit-hash abc123def \
  --output-dir ./matter-master-data
```

### Example 3: Process Multiple Versions

```bash
#!/bin/bash
VERSIONS=("1.3" "1.4" "1.4.1" "master")
CHIP_PATH="~/connectedhomeip"

for version in "${VERSIONS[@]}"; do
  echo "Processing Matter $version..."
  python app.py \
    --chip-path $CHIP_PATH \
    --chip-version-dir $version \
    --output-dir "./output/$version"
done
```

## 🏗️ Project Structure

```
matter-data-model-json-generator/
├── app.py                          # Main CLI application
├── core/                           # Core processing modules
│   ├── xml_parser.py              # XML parsing orchestration
│   └── combine_clusters_devices.py # Data combination logic
├── source_parser/                  # XML parsing components
│   ├── cluster_parser.py          # Cluster XML parser
│   ├── device_parser.py           # Device type XML parser
│   ├── attribute_parser.py        # Attribute parser
│   ├── command_parser.py          # Command parser
│   ├── event_parser.py            # Event parser
│   ├── feature_parser.py          # Feature parser
│   ├── conformance.py             # Conformance logic
│   ├── elements.py                # Data model classes
│   └── serializers.py             # JSON serialization
├── utils/                          # Utility functions
│   ├── file_utils.py              # File operations
│   ├── logger.py                  # Logging setup
│   ├── helper.py                  # Helper functions
│   └── mapping.py                 # Data mappings
├── examples/                       # Usage examples
├── tests/                          # Test suite
├── requirements.txt                # Python dependencies
├── setup.py                       # Package setup
├── LICENSE                        # Apache 2.0 License
└── README.md                      # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/matter-data-model-json-generator.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install in development mode: `pip install -e .[dev]`
6. Run tests: `python -m pytest`

### Code Quality

- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Include docstrings for public functions
- Write tests for new functionality
- Ensure all tests pass before submitting

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/pimpalemahesh/matter-data-model-json-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pimpalemahesh/matter-data-model-json-generator/discussions)
- **Documentation**: [Wiki](https://github.com/pimpalemahesh/matter-data-model-json-generator/wiki)

## 🙏 Acknowledgments

- Matter specification team for the comprehensive data models
- Connected Home over IP (CHIP) project contributors
- The open-source community for tools and libraries

---

**Note**: This tool is designed to work with the official Matter specification XML files. Ensure you have the appropriate rights to access and use the connectedhomeip repository data.
