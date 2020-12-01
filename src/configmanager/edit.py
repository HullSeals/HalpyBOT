"""
HalpyBOT v1.1

edit.py - Write changes to config file

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""

from main import config

async def config_write(module: str, key: str, value):
    config[module][key] = value
    with open('config/config.ini', 'w') as conf:
        config.write(conf)
