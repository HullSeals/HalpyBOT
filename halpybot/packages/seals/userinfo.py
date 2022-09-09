"""
userinfo.py - Fetching information about a registered user.

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from ..database import engine, NoDatabaseConnection


async def whois(subject):
    """Get a Seal's historical information from the Database.

    Args:
        subject (str): The Seal's name being searched

    Returns:
        (str): The details about the Seal, or an error string if not found.

    """
    # Set default values
    u_id, u_cases, u_name, u_regdate, u_distant_worlds, u_distant_worlds_2 = (
        None,
        None,
        None,
        None,
        None,
        None,
    )
    result = None
    connection = engine.raw_connection()
    try:
        args = (subject, 0, 0, 0, 0, 0, 0)
        cursor_obj = connection.cursor()
        cursor_obj.callproc("spWhoIs", args)
        result = list(cursor_obj.fetchall())
        cursor_obj.close()
        connection.commit()
    except NoDatabaseConnection:
        return "Error searching user."
    finally:
        connection.close()
    for res in result:
        u_id, u_cases, u_name, u_regdate, u_distant_worlds = res
        if u_distant_worlds == 1:
            u_distant_worlds_2 = (
                ", is a DW2 Veteran and Founder Seal with registered CMDRs of"
            )
        else:
            u_distant_worlds_2 = ", with registered CMDRs of"

    if u_id is None:
        return "No registered user found by that name!"
    return (
        f"CMDR {subject} has a Seal ID of {u_id}, registered on {u_regdate}{u_distant_worlds_2} {u_name}"
        f", and has been involved with {u_cases} rescues."
    )
