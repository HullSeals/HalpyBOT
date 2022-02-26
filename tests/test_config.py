"""
HalpyBOT v1.5.2

test_config.py - Configuration File module tests

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""
import pytest
import os
from src.packages.configmanager import *


# Does the Config file exist?
@pytest.mark.asyncio
def test_config_exists():
    config_file = os.path.exists("config/config.ini")
    assert config_file is True


# Check critical aspects for value
@pytest.mark.asyncio
async def test_config_value():
    config_values = {  # Essential if you are using NickServ/SASL
        "config['SASL']['username']",
        "config['SASL']['password']",
        # End NickServ/SASL
        "config['IRC']['server']",
        "config['IRC']['server']",
        "config['IRC']['usessl']",
        "config['IRC']['nickname']",
        # If this one is blank, hbot will process everything as a command
        "config['IRC']['commandprefix']",
        "config['IRC']['operline']",
        "config['IRC']['operlinepassword']",
        "config['API Connector']['port']",
        "config['API Connector']['key']",
        "config['API Connector']['key_check_constant']",
        "config['Channels']['channellist']",
        "config['Database']['user']",
        "config['Database']['password']",
        "config['Database']['host']",
        "config['Database']['database']",
        "config['Database']['timeout']",
        "config['Force join command']['joinable']",
        "config['Offline Mode']['enabled']",
        "config['EDSM']['maximum landmark distance']",
        "config['Logging']['cli_level']",
        "config['Logging']['file_level']",
        "config['Logging']['log_file']",
        "config['Facts']['table']",
        "config['Twitter']['enabled']",
        "config['System Monitoring']['failure_button']"}
    for value in config_values:
        assert value is not None


# Can we write to the Config file?
@pytest.mark.asyncio
async def test_config_write():
    prev_value = config['IRC']['usessl']
    config_write('IRC', 'usessl', 'True')
    assert config['IRC']['usessl'] == 'True'
    config_write('IRC', 'usessl', 'False')
    assert config['IRC']['usessl'] == 'False'
    config_write('IRC', 'usessl', prev_value)
    assert config['IRC']['usessl'] == prev_value
