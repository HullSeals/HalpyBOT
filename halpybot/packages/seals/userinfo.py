"""
userinfo.py - Fetching information about a registered user.

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from sqlalchemy.engine import Engine
from sqlalchemy import text
from ..models import Seal


async def whois(engine: Engine, subject: str) -> Seal:
    """Get a Seal's historical information from the Database.

    Args:
        engine (Engine): The database connection engine
        subject (str): The Seal's name being searched

    Returns:
        (Seal): The Seal object

    """
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "CALL spWhoIs(:subject, @sealID, @casecnt, @sealnms, @ircnms, @joined, @dw2, @message)"
            ),
            {"subject": subject},
        )
        results = result.fetchall()
    if not results:
        raise KeyError("No Results Given")
    u_id, u_cases, u_name, u_aliases, u_regdate, u_dw2 = results[0]
    if u_id is None:
        raise ValueError
    return Seal(
        name=subject,
        seal_id=u_id,
        reg_date=u_regdate,
        dw2=u_dw2,
        cmdrs=u_name,
        irc_aliases=u_aliases,
        case_num=u_cases,
    )
