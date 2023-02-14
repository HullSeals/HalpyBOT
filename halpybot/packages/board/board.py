"""
board.py - Internal Case Board

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from datetime import datetime


class Board:
    """
    Internal Case Board - Tracking Cases Cleanly
    """

    def __init__(self):
        """Initalize the Board"""
        self._cases = {}
        self._case_index = None
        self._last_case_time = None

    @property
    def time_last_case(self):
        """Time since the last case started"""
        return self._last_case_time

    def _update_last_index(self):
        """Update the last case time index"""
        self._last_case_time = datetime.now()

    """
    TODO
    1) Create Local Case IDs
    2) Create a Case
    3) Update a Case
    4) Delete a Case
    """
