"""
delayedboard.py - Database interaction for Delayed Board commands

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from sqlalchemy import text
from ..database import engine
from ..utils import strip_non_ascii


class DelayedCase:
    @staticmethod
    async def open(status, message, author):
        """Create a new case on the Delayed Board


        Args:
            status (str): 1 for `needs seals`, 2 for `waiting for seals/client to arrive`
            message (str): Notes for the case
            author (str): Nickname of user who created the case

        Returns:
            (list):

                0 - ID (int): the ID for the created case
                1 - Status (int): `0` if successful, `1` if failed
                2 - Error (str): If status 1, error message

        Raises:
            NoDatabaseConnection: When no connection to the database could be established

        """
        message = strip_non_ascii(message)
        in_args = [int(status), str(message[0]), author, 0, 0, 0]
        out_args = []
        connection = engine.raw_connection()
        try:
            cursor_obj = connection.cursor()
            cursor_obj.callproc("spCreateDelayedCase", in_args)
            results = list(cursor_obj.fetchall())
            cursor_obj.close()
            connection.commit()
        finally:
            connection.close()
        for result in results:
            out_args = result
        out_args = list(out_args)
        out_args.append(bool(message[1]))
        return out_args

    @staticmethod
    async def reopen(case_id, casestat, author):
        """Reopen a previously closed case on the Delayed Board

        Args:
            case_id (int): the ID of the case to be reopened
            casestat (str): New status: 1 for `needs seals`,
                2 for `waiting for seals/client to arrive`
            author (str): Nickname of user

        Returns:
            (list):

                0 - ID (int): ID of the reopened case
                1 - Status (int): `0` if successful, `1` if failed
                2 - Error (str): If status 1, error message

        Raises:
            NoDatabaseConnection: When no connection to the database could be established

        """
        in_args = [int(case_id), int(casestat), author, 0, 0, 0]
        out_args = []
        connection = engine.raw_connection()
        try:
            cursor_obj = connection.cursor()
            cursor_obj.callproc("spReopenDelayedCase", in_args)
            results = list(cursor_obj.fetchall())
            cursor_obj.close()
            connection.commit()
        finally:
            connection.close()
        for result in results:
            out_args = result
        out_args = list(out_args)
        return out_args

    @staticmethod
    async def status(case_id, casestat, author):
        """Update status code of a Delayed Case

        Args:
            case_id (int): the ID of the case to be updated
            casestat (int): New status code: 1 for `needs seals`,
                2 for `waiting for seals/client to arrive`
            author (str): Nickname of user

        Returns:
            (list):

                0 - ID (int): ID of the reopened case
                1 - Status (int): `0` if successful, `1` if failed
                2 - Error (str): If status 1, error message

        Raises:
            NoDatabaseConnection: When no connection to the database could be established

        """
        in_args = [int(case_id), int(casestat), author, 0, 0, 0]
        out_args = []
        connection = engine.raw_connection()
        try:
            cursor_obj = connection.cursor()
            cursor_obj.callproc("spUpdateStatusDelayedCase", in_args)
            results = list(cursor_obj.fetchall())
            cursor_obj.close()
            connection.commit()
        finally:
            connection.close()
        for result in results:
            out_args = result
        out_args = list(out_args)
        return out_args

    @staticmethod
    async def notes(case_id, message, author):
        """Update notes of a Delayed Board case

        Args:
            case_id (int): Delayed Case ID of the case we want to edit
            message (str): new case notes
            author (str): User who invoked command

        Returns:
            (list):

                0 - ID (int): ID of the reopened case
                1 - Status (int): `0` if successful, `1` if failed
                2 - Error (str): If status 1, error message

        Raises:
            NoDatabaseConnection: When no connection to the database could be established

        """
        message = strip_non_ascii(message)
        in_args = [int(case_id), str(message[0]), author, 0, 0, 0]
        out_args = []
        connection = engine.raw_connection()
        try:
            cursor_obj = connection.cursor()
            cursor_obj.callproc("spUpdateMsgDelayedCase", in_args)
            results = list(cursor_obj.fetchall())
            cursor_obj.close()
            connection.commit()
        finally:
            connection.close()
        for result in results:
            out_args = result
        out_args = list(out_args)
        out_args.append(bool(message[1]))
        return out_args

    @staticmethod
    async def check():
        """Check for cases on the Delayed Board

        Returns:
            (int): Number of cases currently opened

        Raises:
            NoDatabaseConnection: When no connection to the database could be established

        """
        # Set default value
        with engine.connect() as database_connection:
            result = database_connection.execute(
                text("SELECT COUNT(ID) FROM casestatus WHERE case_status IN (1, 2)")
            )
            for row in result:
                result = row[0]
        # Return the total amount of open delayed cases on the board
        return result
