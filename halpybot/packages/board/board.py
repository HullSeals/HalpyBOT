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
from ..models import Case, Platform


class Board:
    """
    Internal Case Board - Tracking Cases Cleanly
    """

    def __init__(self, id_range):
        """Initalize the Board"""
        self._cases_by_id: typing.Dict[int, Case] = {}
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
            1: Case(board_id=1, client_name="Bob", platform=Platform(1), system="Delkar"),
            2: Case(board_id=2, client_name="Larry", platform=Platform(1), system="Delkar"),
            4: Case(board_id=3, client_name="John", platform=Platform(1), system="Delkar"),
        }
        self._case_alias_name = {"bob": 1, "larry": 2, "john": 4}
        return

    @property
    async def debug_full_board(self):
        """DEBUG: Load test data into the board"""
        self._cases_by_id = {
            1: Case(board_id=1, client_name="one", platform=Platform(1), system="Delkar"),
            2: Case(board_id=2, client_name="two", platform=Platform(1), system="Delkar"),
            3: Case(board_id=3, client_name="three", platform=Platform(1), system="Delkar"),
            4: Case(board_id=4, client_name="four", platform=Platform(1), system="Delkar"),
            5: Case(board_id=5, client_name="five", platform=Platform(1), system="Delkar"),
            6: Case(board_id=6, client_name="six", platform=Platform(1), system="Delkar"),
            7: Case(board_id=7, client_name="seven", platform=Platform(1), system="Delkar"),
            8: Case(board_id=8, client_name="eight", platform=Platform(1), system="Delkar"),
            9: Case(board_id=9, client_name="nine", platform=Platform(1), system="Delkar"),
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
    def by_id(self) -> dict:
        """Returns the cases_by_id dict"""
        return self._cases_by_id

    @property
    def time_last_case(self) -> typing.Optional[DateTime]:
        """Time since the last case started"""
        return self._last_case_time

    def _update_last_index(self):
        """Update the last case time index"""
        self._last_case_time = now(tz="utc")

    def return_rescue(self, key: typing.Union[str, int]) -> Case:
        """Find a Case given the Client Name or Case ID"""
        if isinstance(key, str) and key in self._case_alias_name.keys():
            return self._cases_by_id[self._case_alias_name[key.casefold()]]
        if isinstance(key, int) and key in self._cases_by_id.keys():
            return self._cases_by_id[key]
        raise KeyError(f"Key {key!r} not found.")

    def __contains__(self, key: typing.Union[str, int]) -> bool:
        if isinstance(key, str):
            return key.casefold() in self._case_alias_name
        if isinstance(key, int):
            return key in self._cases_by_id
        return False

    async def add_case(self, client, platform: Platform, system) -> Case:
        """Create a new Case given the client name"""
        async with self._modlock:
            new_id = self.open_rescue_id
            case = Case(
                board_id=new_id, client_name=client, platform=platform, system=system
            )
            self._update_last_index()
            if case.client_name in self._case_alias_name:
                raise ValueError("Case with Client Name Already Exists")

            self._cases_by_id[new_id] = case
            self._case_alias_name[client] = new_id
            return case

    @asynccontextmanager
    async def mod_case(self, case: Case):
        """
        Modify an existing case'
        TODO: Is this thing on?
        """
        async with self._modlock:
            current_case = case.board_id
            current_client = case.client_name
            del self._cases_by_id[current_case]
            del self._case_alias_name[current_client]
            try:
                yield case
            finally:
                self._cases_by_id[current_case] = case
                self._case_alias_name[current_client] = current_case

    async def del_case(self, case: Case):
        """Delete a Case from the Board"""
        if not isinstance(case, Case):
            raise TypeError
        board_id = case.board_id
        client = case.client_name
        async with self._modlock:
            del self._cases_by_id[board_id]
            del self._case_alias_name[client]

    async def rename_case(self, new_name: str, case: Case):
        """Rename an actively referenced case"""
        # Make Sure we have a Case
        if not isinstance(case, Case):
            raise TypeError
        # Gather old info
        board_id = case.board_id
        old_name = case.client_name
        # Test Old Info
        if new_name in self._case_alias_name:
            raise AssertionError(f"Case already exists under the name {new_name!r}")
        if old_name == new_name:
            raise AssertionError(f"Case Rename Failed. Names Match: {old_name!r}")
        # Update and Continue
        case.client_name = new_name
        async with self._modlock:
            del self._case_alias_name[old_name]
            self._case_alias_name[new_name] = board_id
