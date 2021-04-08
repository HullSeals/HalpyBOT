"""
HalpyBOT v1.4

delayedboard.py - Database interaction for Delayed Board commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from . import DatabaseConnection, NoDatabaseConnection
from ..utils import strip_non_ascii


async def createCase(casestat, message, author):
    """Create a new case on the Delayed Board


    Args:
        casestat (str): 1 for `needs seals`, 2 for `waiting for seals/client to arrive`
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
    in_args = [int(casestat), str(message[0]), author, 0, 0, 0]
    out_args = []
    try:
        db = DatabaseConnection()
        cursor = db.cursor
        cursor.callproc('spCreateDelayedCase', in_args)
        for result in cursor.stored_results():
            out_args.append(result.fetchall())
    except NoDatabaseConnection:
        raise
    out_args = list(out_args[0][0])
    db.close()
    out_args.append(True if message[1] else False)
    return out_args


async def reopenCase(cID, casestat, author):
    """Reopen a previously closed case on the Delayed Board

    Args:
        cID (int): the ID of the case to be reopened
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
    in_args = [int(cID), int(casestat), author, 0, 0, 0]
    out_args = []
    try:
        db = DatabaseConnection()
        cursor = db.cursor
        cursor.callproc('spReopenDelayedCase', in_args)
    except NoDatabaseConnection:
        raise
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    db.close()
    return out_args


async def updateCaseStatus(cID, casestat, author):
    """Update status code of a Delayed Case

    Args:
        cID (int): the ID of the case to be updated
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
    in_args = [int(cID), int(casestat), author, 0, 0, 0]
    out_args = []
    try:
        db = DatabaseConnection()
        cursor = db.cursor
        cursor.callproc('spUpdateStatusDelayedCase', in_args)
    except NoDatabaseConnection:
        raise
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    db.close()
    return out_args


async def updateCaseNotes(cID, message, author):
    """Update notes of a Delayed Board case

    Args:
        cID (int): Delayed Case ID of the case we want to edit
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
    in_args = [int(cID), str(message[0]), author, 0, 0, 0]
    out_args = []
    try:
        db = DatabaseConnection()
        cursor = db.cursor
        cursor.callproc('spUpdateMsgDelayedCase', in_args)
    except NoDatabaseConnection:
        raise
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    out_args.append(True if message[1] else False)
    db.close()
    return out_args

async def caseCheck():
    """Check for cases on the Delayed Board

    Returns:
        (int): Number of cases currently opened

    Raises:
        NoDatabaseConnection: When no connection to the database could be established

    """
    # Set default value
    result = None
    try:
        db = DatabaseConnection()
        cursor = db.cursor
        cursor.execute("SELECT COUNT(ID) "
                       "FROM casestatus "
                       "WHERE case_status IN (1, 2);")
        for res in cursor.fetchall():
            result = res[0]
        db.close()
        # Return the total amount of open delayed cases on the board
        return result
    except NoDatabaseConnection:
        raise
