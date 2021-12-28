"""
HalpyBOT v1.5

userinfo.py - Fetching information about a registered user.

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from ..database import DatabaseConnection, NoDatabaseConnection


async def whois(subject):
    # Set default values
    uID, uCases, uName, uRegdate, uDW, uDW2 = None, None, None, None, None, None
    try:

        with DatabaseConnection() as db:
            cursor = db.cursor()
            args = (subject, 0, 0, 0, 0, 0, 0)
            # Instead of inline code, we call a stored procedure to put some of this work on the database.
            cursor.callproc('spWhoIs', args)
            for res in cursor.stored_results():
                result = res.fetchall()
            for res in result:
                uID, uCases, uName, uRegdate, uDW = res
                if uDW == 1:
                    uDW2 = ", is a DW2 Veteran and Founder Seal with registered CMDRs of"
                else:
                    uDW2 = ", with registered CMDRs of"

    except NoDatabaseConnection:
        return "Error searching user."

    if uID is None:
        return "No registered user found by that name!"
    else:
        return f"CMDR {subject} has a Seal ID of {uID}, registered on {uRegdate}{uDW2} {uName}" \
               f", and has been involved with {uCases} rescues."
