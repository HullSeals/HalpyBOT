"""
HalpyBOT v1.5

facthandler.py - Database interaction for the fact module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from __future__ import annotations
from typing import List, Optional
import json
import re

from ..database import DatabaseConnection, NoDatabaseConnection
from ..configmanager import config
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


class Fact:

    def __init__(self, ID: Optional[int], name: str, lang: str, text: str, author: str):
        """Create a new fact

        Args:
            ID (int or None): Fact ID, if the fact only exists in local storage
                use None
            name (str): Name of the fact
            lang (str): Fact language ISO-639-1 code
            text (str): Fact text
            author (str): Fact author

        """
        self._offline = True if ID is None else False
        self._ID = ID
        self._name = name
        self._lang = lang
        self._default_argument = None
        self._text = self._parse_fact(text)
        self._raw_text = text
        self._author = author

    @property
    def ID(self):
        """Fact ID as stored in DB"""
        return self._ID

    @property
    def name(self):
        """Fact name"""
        return self._name

    @property
    def language(self):
        """ISO-639-1 language code"""
        return self._lang.upper()

    @property
    def default_argument(self):
        """Argument used when none are provided by user"""
        return self._default_argument

    @property
    def text(self):
        """Parsed fact content"""
        return self._text

    @property
    def raw_text(self):
        """Unparsed fact content, including default argument"""
        return self._raw_text

    @property
    def author(self):
        """Fact author"""
        return self._author

    @name.setter
    def name(self, newname: str):
        self._name = newname
        self._write()

    @text.setter
    def text(self, newtext: str):
        self._text = self._parse_fact(newtext)
        self._raw_text = newtext
        self._write()

    def _parse_fact(self, text: str):
        """Parse a fact

        Converts b/i/u to control character and parses default argument.

        Args:
            text (str): Fact text to be parsed

        Returns:
            (str): Parsed fact text

        """
        re_defarg = re.compile(r"({{(?P<defarg>.+)}})(?P<fact>.+)")
        groups = re_defarg.search(text)
        if re.match(re_defarg, text):
            self._default_argument = groups.group('defarg')
        repltable = {"<<BOLD>>": "\u0002",
                     "<<ITALICS>>": "\u001D",
                     "<<UNDERLINE>>": "\u001f",
                     " %n% ": "\n"}
        if self._default_argument:
            text = groups.group('fact')
        for token, new in repltable.items():
            text = text.replace(token, new)
        return text

    def _write(self):
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
            with DatabaseConnection() as db:
                cursor = db.cursor()
                args = (self._name, self._lang.lower(), self._raw_text, self._author, self._ID)
                cursor.execute(f"UPDATE {config['Facts']['table']} "
                               f"SET factName = %s, factLang = %s, factText = %s, "
                               f"factEditedBy = %s "
                               f"WHERE factID = %s", args)
        except NoDatabaseConnection:
            raise FactUpdateError("Fact was probably updated locally but could "
                                  "not be uploaded to the database.")


class FactHandler:

    def __init__(self):
        """Create a new fact handler

        Create a new fact manager object. On creation, this is still
        'empty', and not able to process input. Do this by loading facts
        and attaching it to a command handler.

        """
        self._factCache = {}

    async def get(self, name: str, lang: str = "en") -> Optional[Fact]:
        """Get a fact object by name

        If no language is specified, we get the English fact by default

        Args:
            name (str): Name of the fact, without a -xx language suffix
            lang (str): fact language code as specified in ISO-639-1

        Returns:
            (`Fact` or None) Fact object if exists, else None

        """
        if (name, lang) in self._factCache.keys():
            return self._factCache[name, lang]
        else:
            return None

    async def fetch_facts(self, preserve_current: bool = False):
        """Refresh fact cache.

        If a database connection is available, we will get the facts from there.
        Else, we get it from the backup files.

        Args:
            preserve_current (bool): If True, and database connection is not available,
                we don't attempt to update the fact cache at all and just leave it as it is.

        """
        try:
            await self._from_database()
        except NoDatabaseConnection:
            if not preserve_current:
                await self._from_local()
            raise

    async def _from_database(self):
        """Get facts from database and update the cache"""
        try:
            with DatabaseConnection() as db:
                cursor = db.cursor()
                cursor.execute(f"SELECT factID, factName, factLang, factText, factAuthor "
                               f"FROM {config['Facts']['table']}")
                self._flush_cache()
                for (ID, Name, Lang, Text, Author) in cursor:
                    self._factCache[Name, Lang] = Fact(int(ID), Name, Lang, Text, Author)
        except NoDatabaseConnection:
            raise

    async def _from_local(self):
        """Get facts from local backup file and update the cache"""
        with open("data/facts/backup_facts.json") as jsonfile:
            backupfile = json.load(jsonfile)
        self._flush_cache()
        for fact in backupfile.keys():
            # Get lang and fact. This is stupid, just ignore
            if '-' in fact:
                factname = str(fact).split('-')[0]
                lang = str(fact).split('-')[1]
            else:
                factname = fact
                lang = "en"
            self._factCache[factname, lang] = Fact(None, factname, lang, backupfile[f"{factname}-{lang}"], "OFFLINE")

    def _flush_cache(self):
        """Flush the fact cache. Use with care"""
        self._factCache.clear()

    async def add_fact(self, name: str, lang: str, text: str, author: str):
        """Add a new fact

        If the fact name corresponds to an existing fact in combination
        with the language, or to an existing command, the fact handler refuses
        to create it.

        Args:
            name (str): name of the fact
            lang (str): language code, as specified in ISO-639-1
            text (str): Text of the fact, including formatting
            author (str): Author of the fact

        Raises:
            InvalidFactException: Fact does not have an English version, or fact
                already exists
            NoDatabaseConnection: No connection is available, and fact was not added to the DB
            FactUpdateError: Fact was added, but cache could not be updated.

        """
        if name in Commands.commandList.keys():
            raise InvalidFactException("This fact is already an existing command")
        # Check if we have an English fact:
        if not await self.get(name, 'en') and lang.lower() != 'en':
            raise InvalidFactException("All registered facts must have an English version")
        if (name, lang) in self._factCache:
            raise InvalidFactException("This fact already exists.")
        try:
            with DatabaseConnection() as db:
                cursor = db.cursor()
                cursor.execute(f"INSERT INTO {config['Facts']['table']} "
                               f"(factName, factLang, factText, factAuthor) "
                               f"VALUES (%s, %s, %s, %s);", (name, lang, text, author))
        except NoDatabaseConnection:
            raise
        # Reset the fact handler
        try:
            await self.fetch_facts(preserve_current=True)
        except FactUpdateError:
            raise

    async def lang_by_fact(self, name: str):
        """Get a list of languages a fact exists in

        For a non-existent fact, this will return an empty list

        Args:
            name (str): Name of the fact to be searched for

        Returns:
            (list): List of all languages a fact exists in.

        """
        langlist = []
        for fact in self._factCache.keys():
            if fact[0] == name:
                langlist.append(fact[1])
        return langlist

    async def get_fact_names(self):
        """Get a list of unique facts

        The list is language-independent: if a fact exists in X
        languages it will only be in the list once

        Returns:
            (list): a list of all unique facts

        """
        namelist = []
        for fact in self._factCache.keys():
            if fact[0] in namelist:
                pass
            else:
                namelist.append(fact[0])
        return namelist

    async def delete_fact(self, name: str, lang: str = "en"):
        """Delete a fact

        Fact is immediately deleted from both local storage and the database;
        use with care.

        Args:
            name (str): Name of the fact to be deleted
            lang (str): Fact language ISO-639-1 code. English by default

        Raises:
            NoDatabaseConnection: Raised when entering offline mode

        """
        if lang.lower() == 'en' and len(await self.lang_by_fact(name)) > 1:
            raise FactHandlerError("Cannot delete English fact if other languages "
                                   "are registered for that fact name.")
        try:
            with DatabaseConnection() as db:
                cursor = db.cursor()
                cursor.execute(f"DELETE FROM {config['Facts']['table']} "
                               f"WHERE factID = %s", (self._factCache[name, lang].ID,))
                del self._factCache[name, lang]
        except NoDatabaseConnection:
            raise

    def list(self, lang: Optional[str] = None) -> List[tuple]:
        """Get a list of facts

        Get a list of all facts from internal memory.

        Args:
            lang (str): Fact language ISO-639-1 code. English by default

        Returns:
            (list) a list of all fact names

        """
        if not lang:
            return list(self._factCache.keys())
        else:
            langlist = []
            for fact in self._factCache.keys():
                if fact[1].lower() == lang.lower():
                    langlist.append(fact[0])
            return langlist

    async def fact_formatted(self, fact: tuple, arguments: List[str]):
        """Format a ready-to-be-sent fact

        If no arguments are supplied, we include the default one

        Args:
            fact (tuple): Fact, formatted as (name, lang)
            arguments (list): List of arguments

        Returns:
            (str): Formatted fact text

        Raises:
            FactHandlerError: Fact was not found

        """
        reqfact = self._factCache[fact]
        # Sanity check
        if not reqfact:
            raise FactHandlerError("Fact could not be found, even though it "
                                   "should exist")

        # If we have no args but a default one, send it
        if not arguments and reqfact.default_argument:
            return str(reqfact.default_argument) + str(reqfact.text)

        # If we have arguments add them
        elif arguments:
            return str(' '.join(arguments).strip() + ': ' + reqfact.text)

        # Else (no args, no default arg)
        else:
            return str(reqfact.text)


Facts = FactHandler()
