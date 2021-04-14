"""
HalpyBOT v1.4

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

class FactHandlerError(Exception):
    """
    Base class for fact handler exceptions
    """

class FactUpdateError(FactHandlerError):
    """
    Unable to update a fact attribute to the database
    """

class Fact:

    def __init__(self, ID: Optional[int], name: str, lang: str, text: str, author: str):
        if ID is None:
            self._offline = True
        self._ID = ID
        self._name = name
        self._lang = lang
        self._text = self._parse_fact(text)
        self._raw_text = text
        self._author = author

    @property
    def ID(self):
        return self._ID

    @property
    def name(self):
        return self._name

    @property
    def language(self):
        return self._lang.upper()

    @property
    def text(self):
        return self._text

    @property
    def raw_text(self):
        return self._raw_text

    @property
    def author(self):
        return self._author

    @name.setter
    def name(self, newname: str):
        # TODO check if new name not already a fact/command
        self._name = newname
        self._write()

    @text.setter
    def text(self, newtext: str):
        self._text = self._parse_fact(newtext)
        self._raw_text = newtext
        self._write()

    @staticmethod
    def _parse_fact(text: str):
        repltable = {"<<BOLD>>": "\u0002",
                     "<<ITALICS>>": "\u001D",
                     "<<UNDERLINE>>": "\u001f",
                     " %n% ": "\n"}
        for token, new in repltable.items():
            text = text.replace(token, new)
        return text

    def __del__(self):
        with DatabaseConnection() as db:
            cursor = db.cursor()
            cursor.execute(f"DELETE FROM {config['Facts']['table']} "
                           f"WHERE factID = %s", self._ID)

    def _write(self):
        # Don't write to DB if we're editing an offline fact.
        # We shouldn't ever end up in this situation, anyway
        if self._offline:
            return
        try:
            with DatabaseConnection() as db:
                cursor = db.cursor()
                args = (self._name, self._lang.upper(), self._text, self._author, self._ID)
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

    async def get_fact_object(self, name: str, lang: str = "en") -> Optional[Fact]:
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
        except FactUpdateError:
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
            raise FactUpdateError("Unable to fetch facts from database")

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
            self._factCache[factname, lang] = Fact(None, backupfile[factname], lang, fact, "HalpyBOT OM")

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

        """
        pass

    async def get_fact_languages(self, name: str):
        langlist = []
        for fact in self._factCache.keys():
            if fact[0] == name:
                langlist.append(fact[1])
        return langlist

    async def get_fact_names(self):
        namelist = []
        for fact in self._factCache.keys():
            if fact[0] in namelist:
                pass
            else:
                namelist.append(fact[0])
        return namelist

    async def update_fact(self, name: Optional[str] = None,
                          text: Optional[str] = None):
        """Update a fact name or text

        If no value is specified for name or text, we don't update it.
        It's not possible to change a fact language.

        Args:
            name (str): New name of the fact
            text (str): New text for the fact

        """
        pass

    async def delete_fact(self, name: str, lang: str = "en"):
        """Delete a fact

        Fact is immediately deleted from both local storage and the database;
        use with care.

        Args:
            name (str): Name of the fact to be deleted
            lang (str): Fact language ISO-639-1 code. English by default

        Returns:

        """
        del self._factCache[name, lang]

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
            fact:
            arguments:

        Returns:

        """
        reqfact = self._factCache[fact]
        # Sanity check
        if not reqfact:
            raise FactHandlerError("Fact could not be found, even though it "
                                   "should exist")
        re_defarg = re.compile(r"({{(?P<defarg>.+)}})(?P<fact>.+)")
        groups = re_defarg.search(reqfact.text)

        # Set to True and include timestamp once I regret doing it this way: False

        # If we have no args but a default one, send it
        if not arguments and re.match(re_defarg, reqfact.text):
            return str(groups.group('defarg')) + str(groups.group('fact'))

        # If we have args, throw out the default argument
        elif arguments and re.match(re_defarg, reqfact.text):
            # Yes I could make this simpler but caveman brain understanding more good this way
            return str(' '.join(arguments) + ': ' + groups.group('fact'))

        # If we have arguments add them
        elif arguments:
            return str(' '.join(arguments) + ': ' + reqfact.text)

        # Else (no args, no default arg)
        else:
            return str(reqfact.text)
