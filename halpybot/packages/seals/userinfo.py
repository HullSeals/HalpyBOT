"""
HalpyBOT v1.5.2

userinfo.py - Fetching information about a registered user.

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from ..database import DatabaseConnection, NoDatabaseConnection


async def whois(subject):
    # Set default values
    u_id, u_cases, u_name, u_regdate, u_distant_worlds, u_distant_worlds_2 = (
        None,
        None,
        None,
        None,
        None,
        None,
    )
    try:

        with DatabaseConnection() as db:
            cursor = db.cursor()
            args = (subject, 0, 0, 0, 0, 0, 0)
            # Instead of inline code, we call a stored procedure to put some of this work on the database.
            cursor.callproc("spWhoIs", args)
            for res in cursor.stored_results():
                result = res.fetchall()
            for res in result:
                u_id, u_cases, u_name, u_regdate, u_distant_worlds = res
                if u_distant_worlds == 1:
                    u_distant_worlds_2 = (
                        ", is a DW2 Veteran and Founder Seal with registered CMDRs of"
                    )
                else:
                    u_distant_worlds_2 = ", with registered CMDRs of"

    except NoDatabaseConnection:
        return "Error searching user."

    if u_id is None:
        return "No registered user found by that name!"
    else:
        return (
            f"CMDR {subject} has a Seal ID of {u_id}, registered on {u_regdate}{u_distant_worlds_2} {u_name}"
            f", and has been involved with {u_cases} rescues."
        )
