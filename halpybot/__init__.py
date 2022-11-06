"""
__init__.py - Initilization for HalpyBOT core

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from halpybot.packages.configmanager import config

__version__ = "1.6.4"

DEFAULT_USER_AGENT = (
    "HalpyBOT/"
    + __version__
    + " ("
    + config["IRC"]["nickname"]
    + ") "
    + config["UserAgent"]["agent_comment"]
)
