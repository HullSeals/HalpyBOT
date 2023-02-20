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
from contextlib import asynccontextmanager
from pendulum import now, DateTime


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

    # TODO: Remove Debug Info
    @property
    async def debug_load_board(self):
        """DEBUG: Load test data into the board"""
        self._cases_by_id = {
            1: TempRescue(1, "bob"),
            2: TempRescue(2, "larry"),
            4: TempRescue(4, "john"),
        }
        self._case_alias_name = {"bob": 1, "larry": 2, "john": 4}
        return

    @property
    async def debug_full_board(self):
        """DEBUG: Load test data into the board"""
        self._cases_by_id = {
            1: TempRescue(1, "one"),
            2: TempRescue(2, "two"),
            3: TempRescue(3, "three"),
            4: TempRescue(4, "four"),
            5: TempRescue(5, "five"),
            6: TempRescue(6, "six"),
            7: TempRescue(7, "seven"),
            8: TempRescue(8, "eight"),
            9: TempRescue(9, "nine"),
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
        return

    @property
    async def debug_clear_board(self):
        """DEBUG: clear test data from the board"""
        self._cases_by_id = {}
        self._case_alias_name = {}
        return

    # END DEBUG

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
    def time_last_case(self) -> typing.Optional[DateTime]:
        """Time since the last case started"""
        return self._last_case_time

    def _update_last_index(self):
        """Update the last case time index"""
        self._last_case_time = now(tz="utc")

    def return_rescue(self, key: typing.Union[str, int]) -> TempRescue | None:
        """Find a Case given the Client Name or Case ID"""
        if isinstance(key, str):
            return self._cases_by_id[self._case_alias_name[key.casefold()]]
        if isinstance(key, int):
            return self._cases_by_id[key]
        return None

    def __contains__(self, key: typing.Union[str, int]) -> bool:
        if isinstance(key, str):
            return key.casefold() in self._case_alias_name
        return key in self._cases_by_id

    async def add_case(self, client, **kwargs) -> TempRescue:
        """Create a new Case given the client name"""
        new_id = self.open_rescue_id
        case = TempRescue(new_id, client, **kwargs)
        self._last_case_time = now(tz="utc")
        if case.client in self._case_alias_name:
            raise ValueError("Case with Client Name Already Exists")
        async with self._modlock:
            self._cases_by_id[new_id] = case
            self._case_alias_name[client] = new_id
        return case

    @asynccontextmanager
    async def mod_case(self, case: TempRescue):
        """Modify an existing case"""
        async with self._modlock:
            current_case = case.board_id
            current_client = case.client
            self._cases_by_id.pop(current_case)
            self._case_alias_name.pop(current_client)
            try:
                yield case
            finally:
                self._cases_by_id[current_case] = current_case
                self._case_alias_name[current_client] = current_client

    async def del_case(self, case: TempRescue):
        """Delete a Case from the Board"""
        if isinstance(case, TempRescue):
            board_id = case.board_id
            client = case.client
            async with self._modlock:
                self._cases_by_id.pop(board_id)
                self._case_alias_name.pop(client)
        else:
            raise ValueError
