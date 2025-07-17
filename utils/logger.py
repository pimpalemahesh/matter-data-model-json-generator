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
import logging
import os

# ANSI escape codes for colors


class Colors:
    """ """

    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors and file name to log levels"""

    def __init__(self):
        super().__init__()
        self.FORMATS = {
            logging.DEBUG:
            Colors.BLUE + "DEBUG: %(pathname)s: %(lineno)d: %(message)s" +
            Colors.ENDC,
            logging.INFO:
            Colors.GREEN + "INFO: %(pathname)s: %(lineno)d: %(message)s" +
            Colors.ENDC,
            logging.WARNING:
            Colors.YELLOW + "WARNING: %(pathname)s: %(lineno)d: %(message)s" +
            Colors.ENDC,
            logging.ERROR:
            Colors.RED + "ERROR: %(pathname)s: %(lineno)d: %(message)s" +
            Colors.ENDC,
            logging.CRITICAL:
            Colors.RED + Colors.BOLD +
            "CRITICAL: %(pathname)s: %(lineno)d: %(message)s" + Colors.ENDC,
        }

    def format(self, record):
        """

        :param record:

        """
        # Get the relative path instead of full path
        record.pathname = os.path.relpath(record.pathname)
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger(level="INFO"):
    """Setup and return a logger with colored output

    :param level: Default value = "INFO")

    """
    logger = logging.getLogger("matter_parser")

    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(ColoredFormatter())
    logger.addHandler(ch)
    return logger
