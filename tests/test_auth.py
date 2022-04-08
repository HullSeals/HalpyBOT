"""
HalpyBOT v1.6

test_auth.py - Server authentication module tests

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
"""

from halpybot.server.auth import get_hmac


def test_hmac():
    """Test the creation of a new HMAC object"""
    mac = get_hmac("testHMACstring")
    assert (
        mac.hexdigest()
        == "4b3483adbf2b40ae35f23384674353bb0009d2aa72d5c099a7523067834d0fb8"
    )
