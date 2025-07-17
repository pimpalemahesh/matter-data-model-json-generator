#!/usr/bin/env python3
"""Setup configuration for Matter Data Model JSON Generator."""
import os

from setuptools import find_packages
from setuptools import setup

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh
        if line.strip() and not line.startswith("#")
    ]

# Extract core requirements (exclude dev dependencies)
core_requirements = []
for req in requirements:
    if not any(dev in req.lower()
               for dev in ["pytest", "black", "flake8", "mypy", "sphinx"]):
        core_requirements.append(req)

setup(
    name="matter-data-model-json-generator",
    version="1.0.0",
    author="Mahesh Pimpale",
    author_email="pimpalemahesh2021@gmail.com",
    description=
    "A tool to parse Matter XML data models and generate JSON representations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pimpalemahesh/matter-data-model-json-generator",
    project_urls={
        "Bug Tracker":
        "https://github.com/pimpalemahesh/matter-data-model-json-generator/issues",
        "Documentation":
        "https://github.com/pimpalemahesh/matter-data-model-json-generator/wiki",
        "Source Code":
        "https://github.com/pimpalemahesh/matter-data-model-json-generator",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Text Processing :: Markup :: XML",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=core_requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "matter-json-generator=app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
    keywords="matter, xml, json, parser, iot, smart-home, connectedhomeip",
    zip_safe=False,
)
