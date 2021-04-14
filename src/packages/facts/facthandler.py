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
        self._text = text
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
    def author(self):
        return self._author

    @name.setter
    def name(self, newname: str):
        # TODO check if new name not already a fact/command
        self._name = newname
        self._write()

    @text.setter
    def text(self, newtext: str):
        self._text = newtext
        self._write()

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
        self.factCache = {}

    async def get_fact_object(self, name: str, lang: str = "en") -> Optional[Fact]:
        """Get a fact object by name

        If no language is specified, we get the English fact by default

        Args:
            name (str): Name of the fact, without a -xx language suffix
            lang (str): fact language code as specified in ISO-639-1

        Returns:
            (`Fact` or None) Fact object if exists, else None

        """
        if name in self.factCache.keys():
            return self.factCache[name]
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
                    self.factCache[[Name, Lang]] = Fact(int(ID), Name, Lang, Text, Author)
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
            self.factCache[factname, lang] = Fact(None, backupfile[factname], lang, fact, "HalpyBOT OM")

    def _flush_cache(self):
        """Flush the fact cache. Use with care"""
        self.factCache.clear()

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
        pass

    async def list(self, lang: Optional[str] = "en") -> List[str]:
        """Get a list of facts

        Get a list of all facts from internal memory.

        Args:
            lang (str): Fact language ISO-639-1 code. English by default

        Returns:
            (list) a list of all fact names

        """
        pass

async def fact_from_message() -> Optional[Fact]:
    pass
