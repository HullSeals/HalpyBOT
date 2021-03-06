"""
HalpyBOT v1.2

delayedboard.py - Database interaction for Delayed Board commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from . import DatabaseConnection
from ..utils.utils import strip_non_ascii


async def create_delayed_case(casestat, message, author):
    db = DatabaseConnection()
    # FIXME quickfix
    if not hasattr(db, "cnx"):
        return
    cursor = db.cursor
    message = strip_non_ascii(message)
    in_args = [int(casestat), str(message[0]), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spCreateDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    out_args.append(True if message[1] else False)
    db.close()
    return out_args


async def reopen_delayed_case(cID, casestat, author):
    db = DatabaseConnection()
    # FIXME quickfix
    if not hasattr(db, "cnx"):
        return
    cursor = db.cursor
    in_args = [int(cID), int(casestat), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spReopenDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    db.close()
    return out_args


async def update_delayed_status(cID, casestat, author):
    db = DatabaseConnection()
    # FIXME quickfix
    if not hasattr(db, "cnx"):
        return
    cursor = db.cursor
    in_args = [int(cID), int(casestat), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spUpdateStatusDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    db.close()
    return out_args


async def update_delayed_notes(cID, message, author):
    db = DatabaseConnection()
    # FIXME quickfix
    if not hasattr(db, "cnx"):
        return
    cursor = db.cursor
    message = strip_non_ascii(message)
    in_args = [int(cID), str(message[0]), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spUpdateMsgDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    out_args.append(True if message[1] else False)
    db.close()
    return out_args

async def check_delayed_cases():
    db = DatabaseConnection()
    # FIXME quickfix
    if not hasattr(db, "cnx"):
        return
    cursor = db.cursor
    cursor.execute("SELECT COUNT(ID) "
                   "FROM casestatus "
                   "WHERE case_status IN (1, 2);")
    for res in cursor.fetchall():
        result = res[0]
    # Return the total amount of open delayed cases on the board
    return result

