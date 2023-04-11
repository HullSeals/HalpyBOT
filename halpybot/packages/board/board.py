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

import enum
import typing
import functools
import itertools
from asyncio import Lock
from attrs import evolve
from pendulum import now, DateTime
from ..exceptions import CaseAlreadyExists
from ..models import Case, Platform, CaseType, Status


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
    def by_id(self) -> typing.Dict[int, Case]:
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
        if isinstance(key, str):
            return self._cases_by_id[self._case_alias_name[key.casefold()]]
        if isinstance(key, int):
            return self._cases_by_id[key]
        raise KeyError(f"Key {key!r} not found.")

    def __contains__(self, key: typing.Union[str, int]) -> bool:
        if isinstance(key, int):
            return key in self._cases_by_id
        if isinstance(key.casefold(), str):
            return key in self._case_alias_name
        return False

    async def add_case(
        self, client: str, platform: Platform, system: str, case_type: CaseType
    ) -> Case:
        """Create a new Case given the client name"""
        async with self._modlock:
            new_id = self.open_rescue_id
            case = Case(
                board_id=new_id,
                client_name=client,
                platform=platform,
                system=system,
                case_type=case_type,
            )
            self._update_last_index()
            if case.client_name.casefold() in self._case_alias_name:
                raise CaseAlreadyExists("Case with Client Name Already Exists")

            self._cases_by_id[new_id] = case
            self._case_alias_name[client.casefold()] = new_id
            return case

    @functools.wraps(evolve)
    async def mod_case(
        self, case_id: int, action: str = None, sender: str = None, **kwargs
    ):
        """
        Modify an existing case
        """
        # Gather the Case Information
        case: Case = self.return_rescue(case_id)
        curr_time = now(tz="UTC")
        current_case_notes = case.case_notes

        # Prep the new notes
        if action:
            for key, item in kwargs.items():
                oldkey = getattr(case, key)
                if getattr(case, key) == item:
                    raise ValueError(f"{action} is already set to {item}.")
                # Translate Enums into Human-Notes
                if isinstance(item, enum.Enum):
                    item = item.name.replace("_", " ")
                    oldkey = getattr(case, key).name.replace("_", " ")
                notes = f"{action} set to {item} from {oldkey} by {sender} at {curr_time.to_time_string()}"
                current_case_notes.append(notes)

        # Update the Case
        new_case = evolve(
            self._cases_by_id[case_id],
            updated_time=curr_time,
            case_notes=current_case_notes,
            **kwargs,
        )
        self._cases_by_id[case_id] = new_case

    @functools.wraps(evolve)
    async def mod_case_notes(self, case_id: int, new_notes: typing.List[str]):
        """
        Replace the notes of an existing rescue
        """
        # Update the Case
        new_case = evolve(
            self._cases_by_id[case_id],
            updated_time=now(tz="UTC"),
            case_notes=new_notes,
        )
        self._cases_by_id[case_id] = new_case

    async def del_case(self, case: Case):
        """Delete a Case from the Board"""
        if not isinstance(case, Case):
            raise TypeError
        board_id = case.board_id
        client = case.client_name
        async with self._modlock:
            del self._cases_by_id[board_id]
            del self._case_alias_name[client.casefold()]

    async def rename_case(self, new_name: str, case: Case, sender: str):
        """Rename an actively referenced case"""
        # Make Sure we have a Case
        if not isinstance(case, Case):
            raise TypeError
        # Gather old info
        board_id = case.board_id
        old_name = case.client_name
        # Test Old Info
        if new_name.casefold() in self._case_alias_name:
            raise CaseAlreadyExists
        if old_name.casefold() == new_name.casefold():
            raise AssertionError(f"Case Rename Failed. Names Match: {old_name!r}")
        # Update and Continue
        name_kwarg = {"client_name": new_name}
        action = "Client Name"
        try:
            await self.mod_case(board_id, action, sender, **name_kwarg)
        except CaseAlreadyExists:
            raise
        async with self._modlock:
            del self._case_alias_name[old_name.casefold()]
            self._case_alias_name[new_name.casefold()] = board_id
