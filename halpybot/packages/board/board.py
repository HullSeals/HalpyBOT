"""
This file uses Open Source components.
You can find the source code of their open source projects along with license
information below. We acknowledge and are grateful to these developers for their contributions to open source.

Project: SPARK / pipsqueak3 https://github.com/FuelRats/pipsqueak3
License: https://github.com/FuelRats/pipsqueak3/blob/develop/LICENSE

BSD 3-Clause License
Copyright (c) 2018, The Fuel Rats Mischief
All rights reserved.

board.py - Internal Case Board

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from __future__ import annotations
import typing
import itertools
from asyncio import Lock
from pendulum import now


class TempRescue:
    """TODO: Replace with Real Rescue Type"""

    def __init__(self, case_id, client, **kwargs):
        self.board_id = case_id
        self.client = client


class Board:
    """
    Internal Case Board - Tracking Cases Cleanly
    """

    def __init__(self, id_range):
        """Initalize the Board"""
        self._cases_by_id: typing.Dict[int, TempRescue] = {}
        self._case_alias_name: typing.Dict[str, int] = {}
        self._next_case_counter = itertools.count(start=1)
        self._last_case_time = None
        self._modlock = Lock()
        self._id_range: int = id_range

    @property
    async def debug_load_board(self):
        """DEBUG: Load test data into the board"""
        self._cases_by_id = {
            1: TempRescue(),
            2: TempRescue(),
            4: TempRescue(),
        }
        self._case_alias_name = {"bob": 1, "larry": 2, "john": 4}
        return

    @property
    async def debug_full_board(self):
        """DEBUG: Load test data into the board"""
        self._cases_by_id = {
            1: TempRescue(),
            2: TempRescue(),
            3: TempRescue(),
            4: TempRescue(),
            5: TempRescue(),
            6: TempRescue(),
            7: TempRescue(),
            8: TempRescue(),
            9: TempRescue(),
        }
        self._case_alias_name = {
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
        }

    @property
    async def debug_clear_board(self):
        """DEBUG: clear test data from the board"""
        self._cases_by_id = {}
        self._case_alias_name = {}

    @property
    def _open_rescue_id(self) -> int:
        """Returns the next unsed case ID"""
        return next(itertools.filterfalse(self.__contains__, self._next_case_counter))

    @property
    def open_rescue_id(self) -> int:
        """Returns the next valid Case ID"""
        next_id = self._open_rescue_id
        overflow_index = next_id >= self._id_range
        if overflow_index:
            self._next_case_counter = itertools.count(start=1)
            return self._open_rescue_id
        return next_id

    @property
    def time_last_case(self):
        """Time since the last case started"""
        return self._last_case_time

    def _update_last_index(self):
        """Update the last case time index"""
        self._last_case_time = now(tz="utc")

    # TODO: Do we need this?
    def __getitem__(self, key: typing.Union[str, int]) -> TempRescue | None:
        if isinstance(key, str):
            return self._cases_by_id[self._case_alias_name[key.casefold()]]
        if isinstance(key, int):
            return self._cases_by_id[key]
        return None

    def __contains__(self, key: typing.Union[str, int]) -> bool:
        if isinstance(key, str):
            return key.casefold() in self._case_alias_name
        return key in self._cases_by_id

    async def new_rescue(self, client, **kwargs):
        new_id = self.open_rescue_id
        case = TempRescue(new_id, client, **kwargs)
        self._last_case_time = now(tz="utc")
        async with self._modlock:
            self._cases_by_id[new_id] = case
            self._case_alias_name[client] = new_id

    async def mod_rescue(self):
        pass

    async def del_rescue(self, case: TempRescue):
        if isinstance(case, TempRescue):
            board_id = case.board_id
            client = case.client
        async with self._modlock:
            self._cases_by_id.pop(board_id)
            self._case_alias_name.pop(client)

    """
    TODO
    2) Create a Case
    3) Update a Case
    4) Delete a Case
    """
