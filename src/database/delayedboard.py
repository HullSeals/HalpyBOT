"""
HalpyBOT v1.1

delayedboard.py - Database interaction for Delayed Board commands

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from . import cursor


async def create_delayed_case(casestat, message: str, author: str):
    in_args = [int(casestat), str(message), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spCreateDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    return out_args


async def reopen_delayed_case(cID, casestat, author):
    in_args = [int(cID), int(casestat), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spReopenDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    return out_args


async def update_delayed_status(cID, casestat, author):
    in_args = [int(cID), int(casestat), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spUpdateStatusDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    return out_args


async def update_delayed_notes(cID, message, author):
    in_args = [int(cID), str(message), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spUpdateMsgDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    return out_args
