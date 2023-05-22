"""
test_bot.py - HalpyBOT and Configuration Tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from halpybot.packages.ircclient import configure_client, HalpyBOT


def test_config_client():
    """Test if an instance of the HalpyBOT class is returned"""
    returned_client = configure_client()
    assert isinstance(returned_client, HalpyBOT)
