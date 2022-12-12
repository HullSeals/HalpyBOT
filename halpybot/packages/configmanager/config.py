"""
config.py - Configuration manager

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import configparser
from loguru import logger
from halpybot.halpyconfig import HalpyConfig

config: HalpyConfig = HalpyConfig()


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
    raise NotImplementedError("# TODO") # TODO
    logger.info("{module}, {key} set to {value}", module=module, key=key, value=value)
    config[module][key] = value
    try:
        with open("config/config.ini", "w", encoding="UTF-8") as conf:
            config.write(conf)
    except (FileNotFoundError, PermissionError) as ex:
        logger.exception("Error writing value to config file. Check permissions?")
        raise ConfigException from ex
