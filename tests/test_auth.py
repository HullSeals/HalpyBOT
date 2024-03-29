"""
test_auth.py - Server authentication module tests

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from halpybot.server.auth import get_hmac


def test_hmac():
    """Test the creation of a new HMAC object"""
    mac = get_hmac("testHMACstring")
    assert (
        mac.hexdigest()
        == "4b3483adbf2b40ae35f23384674353bb0009d2aa72d5c099a7523067834d0fb8"
    )
