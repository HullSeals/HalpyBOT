"""
test_config.py - Configuration File module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import os
import pytest
from halpybot import config


def test_config_exists():
    """Test that the config file exists. Without it, you aren't getting far."""
    config_file = os.path.exists("config/config.ini")
    assert config_file
