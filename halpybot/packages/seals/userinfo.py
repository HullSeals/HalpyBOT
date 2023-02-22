"""
userinfo.py - Fetching information about a registered user.

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from sqlalchemy.engine import Engine
from ..models import Seal


async def whois(engine: Engine, subject):
    """Get a Seal's historical information from the Database.

    Args:
        engine (Engine): The database connection engine
        subject (str): The Seal's name being searched

    Returns:
        (Seal): The Seal object

    """
    connection = engine.raw_connection()
    args = (subject, 0, 0, 0, 0, 0, 0)
    cursor_obj = connection.cursor()
    cursor_obj.callproc("spWhoIs", args)
    result = list(cursor_obj.fetchall())
    cursor_obj.close()
    connection.commit()
    connection.close()
    if not result:
        raise KeyError("No Results Given")
    for res in result:
        u_id, u_cases, u_name, u_regdate, u_dw2 = res
        if u_id is None:
            raise ValueError
        seal = Seal(
            name=subject,
            seal_id=u_id,
            reg_date=u_regdate,
            dw2=u_dw2,
            aliases=u_name,
            case_num=u_cases,
        )
        return seal
