"""
HalpyBOT v1.3

utils.py - miscellaneous utility functions

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


async def get_time_seconds(time: str):
    pattern = re.compile("(?P<hour>\d+):(?P<minutes>\d+):(?P<seconds>\d+)")
    if not re.match(pattern, time):
        raise ValueError("get_time_seconds input does not match hh:mm:ss format")
    res = pattern.search(time)
    counter = 0
    conversionTable = {
        "hour": 3600,
        "minutes": 60,
        "seconds": 1
    }
    for unit in conversionTable.keys():
        value = int(res.group(unit))
        counter += value * conversionTable[unit]
    return str(counter)
