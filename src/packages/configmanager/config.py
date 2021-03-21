"""
HalpyBOT v1.3

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

async def config_write(module: str, key: str, value):
    logging.info(f"{module}, {key} set to {value}")
    config[module][key] = value
    with open('config/config.ini', 'w') as conf:
        config.write(conf)