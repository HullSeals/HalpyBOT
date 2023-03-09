"""
facthandler.py - Database interaction for the fact module

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
from typing import List, Optional, Dict, Tuple
import json
import re
from attrs import define, field
from attr import ib
from loguru import logger
from sqlalchemy import text, engine
from halpybot import config
from ..database import NoDatabaseConnection, test_database_connection
from ..command import Commands


class FactHandlerError(Exception):
    """
    Base class for fact handler exceptions
    """


class FactUpdateError(FactHandlerError):
    """
    Unable to update a fact attribute to the database
    """


class InvalidFactException(FactHandlerError):
    """
    Raised when an invalid fact is created
    """


@define
class Fact:
    """
    Create a new fact
        Args:
            fact_id (int or None): Fact ID, if the fact only exists in local storage, use None
            name (str): Name of the fact
            lang (str): Fact language ISO-639-1 code
            fact_text (str): Fact fact_text
            author (str): Fact author
    """

    fact_id: Optional[int]
    name: str
    lang: str
    fact_text: str
    author: str

    default_argument: Optional[str] = ib(init=False, default=None)
    _offline: bool = ib(init=False, default=False)
    _text: str = ib(init=False)
    _raw_text: str = ib(init=False)

    def __attrs_post_init__(self):
        self._offline = bool(self.fact_id is None)
        self.default_argument = None
        self._text = self._parse_fact(self.fact_text)
        self._raw_text = self.fact_text

    @property
    def language(self):
        """ISO-639-1 language code"""
        return self.lang.upper()

    @property
    def text(self):
        """Parsed fact content"""
        return self._text

    @property
    def raw_text(self):
        """Unparsed fact content, including default argument"""
        return self._raw_text

    def _parse_fact(self, fact_text: str) -> str:
        """Parse a fact

        Converts b/i/u to control character and parses default argument.

        Args:
            fact_text (str): Fact text to be parsed

        Returns:
            (str): Parsed fact text

        """
        re_defarg = re.compile(r"({{(?P<defarg>.+)}})(?P<fact>.+)")
        groups = re_defarg.search(fact_text)
        if re.match(re_defarg, fact_text):
            self.default_argument = groups.group("defarg")
        repltable = {
            "<<BOLD>>": "\u0002",
            "<<ITALICS>>": "\u001D",
            "<<UNDERLINE>>": "\u001f",
            " %n% ": "\n",
        }
        if self.default_argument:
            fact_text = groups.group("fact")
        for token, new in repltable.items():
            fact_text = fact_text.replace(token, new)
        return fact_text

    def _write(self, db_engine: engine.Engine):
        """Write changes to a fact to the database

        Raises:
            NoDatabaseConnection: When entering offline mode
            FactUpdateError: Raised when attempting to update a
                fact that the bot considers to only exist in local
                storage.

        """
        # Don't write to DB if we're editing an offline fact.
        # We shouldn't ever end up in this situation, anyway
        if self._offline:
            raise FactUpdateError
        try:
            with db_engine.connect() as database_connection:
                database_connection.execute(
                    text(
                        f"UPDATE {config.facts.table}"
                        f"SET factName = :fact_name, factLang = :fact_lang, factText = :fact_text, "
                        f"factEditedBy = :fact_by "
                        f"WHERE factID = :fact_id"
                    ),
                    fact_name=self.name,
                    fact_lang=self.lang.casefold(),
                    fact_text=self._raw_text,
                    fact_author=self.author,
                    fact_id=self.fact_id,
                )
        except NoDatabaseConnection:
            logger.exception("No database connection. Unable to update fact.")
            raise FactUpdateError(
                "Fact was probably updated locally but could "
                "not be uploaded to the database."
            ) from NoDatabaseConnection


@define
class FactHandler:
    """Create a new fact handler

    Create a new fact manager object. On creation, this is still
    'empty', and not able to process input. Do this by loading facts
    and attaching it to a command handler.

    """

    _fact_cache: Dict[Tuple[str, str], Fact] = field(factory=dict)

    async def get(self, name: str, lang: str = "en") -> Optional[Fact]:
        """Get a fact object by name

        If no language is specified, we get the English fact by default

        Args:
            name (str): Name of the fact, without a -xx language suffix
            lang (str): fact language code as specified in ISO-639-1

        Returns:
            (`Fact` or None) Fact object if exists, else None

        """
        if (name, lang) in self._fact_cache:
            return self._fact_cache[name, lang]
        return None

    async def fetch_facts(
        self, db_engine: engine.Engine, preserve_current: bool = False
    ):
        """Refresh fact cache.

        If a database connection is available, we will get the facts from there.
        Else, we get it from the backup files.

        Args:
            db_engine (engine.Engine): DBAPI Engine
            preserve_current (bool): If True, and database connection is not available,
                we don't attempt to update the fact cache at all and just leave it as it is.

        """
        try:
            await test_database_connection(db_engine)
            await self._from_database(db_engine)
        except NoDatabaseConnection:
            logger.exception(
                "Could not fetch facts from DB, backup file loaded and entering OM"
            )
            if not preserve_current:
                await self._from_local()

    async def _from_database(self, db_engine: engine.Engine):
        """Get facts from database and update the cache"""
        with db_engine.connect() as database_connection:
            result = database_connection.execute(
                text(
                    f"SELECT factID, factName, factLang, factText, factAuthor "
                    f"FROM {config.facts.table}"
                )
            )
            self._flush_cache()
            for fact_id, fact_name, fact_lang, fact_text, fact_author in result:
                self._fact_cache[fact_name, fact_lang] = Fact(
                    int(fact_id), fact_name, fact_lang, fact_text, fact_author
                )

    async def _from_local(self):
        """Get facts from local backup file and update the cache"""
        with open("data/facts/backup_facts.json", encoding="UTF-8") as jsonfile:
            backupfile = json.load(jsonfile)
        self._flush_cache()
        for fact in backupfile.keys():
            # Get lang and fact. This is stupid, just ignore
            if "-" in fact:
                factname = str(fact).split("-", maxsplit=1)[0]
                lang = str(fact).split("-", maxsplit=1)[1]
            else:
                factname = fact
                lang = "en"
            self._fact_cache[factname, lang] = Fact(
                None, factname, lang, backupfile[f"{factname}-{lang}"], "OFFLINE"
            )

    def _flush_cache(self):
        """Flush the fact cache. Use with care"""
        self._fact_cache.clear()

    async def add_fact(
        self,
        db_engine: engine.Engine,
        name: str,
        lang: str,
        fact_text: str,
        author: str,
    ):
        """Add a new fact

        If the fact name corresponds to an existing fact in combination
        with the language, or to an existing command, the fact handler refuses
        to create it.

        Args:
            db_engine (engine.Engine): DBAPI Engine
            name (str): name of the fact
            lang (str): language code, as specified in ISO-639-1
            fact_text (str): Text of the fact, including formatting
            author (str): Author of the fact

        Raises:
            InvalidFactException: Fact does not have an English version, or fact
                already exists
            NoDatabaseConnection: No connection is available, and fact was not added to the DB
            FactUpdateError: Fact was added, but cache could not be updated.

        """
        if name in Commands.command_list:
            raise InvalidFactException("This fact is already an existing command")
        # Check if we have an English fact:
        if not await self.get(name) and lang.casefold() != "en":
            raise InvalidFactException(
                "All registered facts must have an English version"
            )
        if (name, lang) in self._fact_cache:
            raise InvalidFactException("This fact already exists.")
        with db_engine.connect() as database_connection:
            database_connection.execute(
                text(
                    f"INSERT INTO {config.facts.table} "
                    f"(factName, factLang, factText, factAuthor) "
                    f"VALUES (:name, :lang, :fact_text, :author);"
                ),
                name=name,
                lang=lang,
                fact_text=fact_text,
                author=author,
            )
        # Reset the fact handler
        await self.fetch_facts(db_engine, preserve_current=True)

    async def lang_by_fact(self, name: str) -> List[str]:
        """Get a list of languages a fact exists in

        For a non-existent fact, this will return an empty list

        Args:
            name (str): Name of the fact to be searched for

        Returns:
            (list): List of all languages a fact exists in.

        """
        langlist = []
        for fact in self._fact_cache:
            if fact[0] == name:
                langlist.append(fact[1])
        return langlist

    async def get_fact_names(self) -> List[str]:
        """Get a list of unique facts

        The list is language-independent: if a fact exists in X
        languages it will only be in the list once

        Returns:
            (list): a list of all unique facts

        """
        namelist = []
        for fact in self._fact_cache:
            if fact[0] in namelist:
                pass
            else:
                namelist.append(fact[0])
        return namelist

    async def delete_fact(self, db_engine: engine.Engine, name: str, lang: str = "en"):
        """Delete a fact

        Fact is immediately deleted from both local storage and the database;
        use with care.

        Args:
            db_engine (engine.Engine): DBAPI Engine
            name (str): Name of the fact to be deleted
            lang (str): Fact language ISO-639-1 code. English by default

        Raises:
            NoDatabaseConnection: Raised when entering offline mode

        """
        if lang.casefold() == "en" and len(await self.lang_by_fact(name)) > 1:
            raise FactHandlerError(
                "Cannot delete English fact if other languages "
                "are registered for that fact name."
            )
        with db_engine.connect() as database_connection:
            database_connection.execute(
                text(f"DELETE FROM {config.facts.table} WHERE factID = :fact_id"),
                fact_id=self._fact_cache[name, lang].fact_id,
            )
            del self._fact_cache[name, lang]

    def list(self, lang: Optional[str] = None) -> list[tuple[str, str]] | list[str]:
        """Get a list of facts

        Get a list of all facts from internal memory.

        Args:
            lang (str): Fact language ISO-639-1 code. English by default

        Returns:
            (list) a list of all fact names

        """
        if not lang:
            return list(self._fact_cache.keys())
        langlist = []
        for fact in self._fact_cache:
            if fact[1].casefold() == lang.casefold():
                langlist.append(fact[0])
        print(langlist)
        return langlist

    async def fact_formatted(self, fact: tuple, arguments: List[str]) -> str:
        """Format a ready-to-be-sent fact

        If no arguments are supplied, we include the default one

        Args:
            fact (tuple): Fact, formatted as (name, lang)
            arguments (list): List of arguments

        Returns:
            (str): Formatted fact fact_text

        Raises:
            FactHandlerError: Fact was not found

        """
        reqfact: Fact = self._fact_cache[fact]
        # Sanity check
        if not reqfact:
            raise FactHandlerError(
                "Fact could not be found, even though it should exist"
            )

        # If we have no args but a default one, send it
        if not arguments and reqfact.default_argument:
            return str(reqfact.default_argument) + str(reqfact.text)

        # If we have arguments add them
        if arguments:
            return str(" ".join(arguments).strip() + ": " + reqfact.text)

        # Else (no args, no default arg)
        return str(reqfact.text)
