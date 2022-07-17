"""
test_config.py - Configuration File module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import os
import pytest
from halpybot.packages.configmanager import config, config_write


def test_config_exists():
    """Test that the config file exists. Without it, you aren't getting far."""
    config_file = os.path.exists("config/config.ini")
    assert config_file


@pytest.mark.asyncio
async def test_config_write():
    """Test that the config file is writable"""
    prev_value = config["IRC"]["usessl"]
    config_write("IRC", "usessl", "True")
    assert config["IRC"]["usessl"] == "True"
    config_write("IRC", "usessl", "False")
    assert config["IRC"]["usessl"] == "False"
    config_write("IRC", "usessl", prev_value)
    assert config["IRC"]["usessl"] == prev_value
