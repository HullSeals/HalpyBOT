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


@pytest.mark.asyncio
@pytest.mark.xfail("config_write needs to be rewritten for this to work.")
async def test_config_write():
    """Test that the config file is writable"""
    # TODO: fix config_write
    prev_value = config.irc.use_ssl
    config_write("IRC", "usessl", "True")
    assert config.irc.use_ssl == "True"
    config_write("IRC", "usessl", "False")
    assert config.irc.use_ssl == "False"
    config_write("IRC", "usessl", prev_value)
    assert config.irc.use_ssl == prev_value
