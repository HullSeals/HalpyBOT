"""
seal.py - Who are you, again?

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from typing import Optional, List, Tuple
from attrs import define
from .case import Platform


@define(frozen=True)
class Seal:
    """Define our Seal"""

    name: str
    seal_id: int
    case_num: int
    cmdrs: Optional[List[Tuple[str, Platform]]]
    irc_aliases: Optional[List[str]]
    reg_date: str
    dw2: bool

    @property
    def dw2_history(self) -> str:
        """Is the Seal a DW2 vet?"""
        if self.dw2:
            return ", is a DW2 Veteran and Founder Seal with registered CMDRs of"
        return ", with registered CMDRs of"

    @property
    def format_cmdrs(self) -> str:
        """Return the list of CMDRs and Platforms"""
        cmdr_str: str = ""
        for cmdrpair in self.cmdrs:
            cmdr = cmdrpair[0]
            plt: Platform = cmdrpair[1]
            if plt in (
                Platform.ODYSSEY,
                Platform.LEGACY_HORIZONS,
                Platform.LIVE_HORIZONS,
            ):
                pltstr = "PC"
            else:
                pltstr = plt.name

            cmdr_str += f"{cmdr} ({pltstr}), "
        return cmdr_str
