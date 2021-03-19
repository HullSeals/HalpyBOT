"""
HalpyBOT v1.2.3

utils.py - miscellaneous functions

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import re


def strip_non_ascii(string: str):
    res = re.subn(r'[^\x00-\x7f]', r'', string)
    if res != (string, 0):
        # Return new string and True if characters were removed
        return res[0], True
    else:
        return res[0], False
