"""
HalpyBOT v1.4.2

config.py - Configuration manager

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import logging
import configparser

config = configparser.ConfigParser()
config.read('config/config.ini')

class ConfigException(Exception):
    """Base class for configuration errors"""

class ConfigWriteError(ConfigException):
    """Unable to write to config file"""

class ConfigValidationFailure(ConfigException):
    """One or more required configuration entries are not present"""

def config_write(module: str, key: str, value):
    """Write a value to the configuration file

    Args:
        module (str): The config module you want to write to
        key (str): The config entry you want to edit
        value (str): New value

    """
    logging.info(f"{module}, {key} set to {value}")
    config[module][key] = value
    try:
        with open('config/config.ini', 'w') as conf:
            config.write(conf)
    except (FileNotFoundError, PermissionError) as ex:
        raise ConfigException(str(ex))
