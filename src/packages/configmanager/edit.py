"""
HalpyBOT v1.2

edit.py - Write changes to config file

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from main import config
import logging

async def config_write(module: str, key: str, value):
    logging.info(f"{module}, {key} set to {value}")
    config[module][key] = value
    with open('config/config.ini', 'w') as conf:
        config.write(conf)
