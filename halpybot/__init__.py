"""
__init__.py - Initilization for HalpyBOT core

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from .halpyconfig import HalpyConfig

# this is where the magic happens. 😇
config = HalpyConfig()


#
__version__ = "2.0.0-alpha"

DEFAULT_USER_AGENT = (
    f"HalpyBot/{__version__}({config.irc.nickname})({config.user_agent.agent_comment})"
)
