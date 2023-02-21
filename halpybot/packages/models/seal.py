"""
seal.py - Who are you, again?

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from typing import Optional, List
from attr import dataclass


@dataclass
class Seal:
    """Define our Seal"""

    name: str
    seal_id: int
    reg_date: str
    dw2: bool
    aliases: Optional[List[str]]
    case_num: int

    @property
    def dw2_history(self):
        """Is the Seal a DW2 vet?"""
        if self.dw2:
            return ", is a DW2 Veteran and Founder Seal with registered CMDRs of"
        return ", with registered CMDRs of"
