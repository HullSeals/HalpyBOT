"""
HalpyBOT v1.6

config.py - Configuration manager

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import configparser
from loguru import logger


config = configparser.ConfigParser()
config.read("config/config.ini")


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
    logger.info("{module}, {key} set to {value}", module=module, key=key, value=value)
    config[module][key] = value
    try:
        with open("config/config.ini", "w", encoding="UTF-8") as conf:
            config.write(conf)
    except (FileNotFoundError, PermissionError) as ex:
        raise ConfigException from ex
