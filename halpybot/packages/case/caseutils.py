"""
caseutils.py - Crunching the Numbers for Case Information

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import re
from typing import Dict
from pendulum import now
from ..ircclient import HalpyBOT
from ..models import Case, Platform


async def format_case_details(case: Case) -> str:
    """Format case information in a ready-to-be-sent format

    Args:
        case: The Case object in question, from the Case Board

    Returns:
        (str): Fully formatted announcement
    """
    updated = now(tz="utc").diff(case.updated_time).in_words()
    created = now(tz="utc").diff(case.creation_time).in_words()
    plt = re.sub("_", " ", case.platform.name)
    message = (
        f"Here's the case listing for Case ID {case.board_id}:\n "
        f"General Details: \n"
        f"    Client: {case.client_name}\n"
        f"    System: {case.system}\n"
        f"    Platform: {plt}\n"
        f"    Case Created: {created} ago\n"
        f"    Case Updated: {updated} ago\n"
        f"    Case Status: {case.status.name}\n"
        f"    Client Welcomed: {'Yes' if case.welcomed else 'No'}\n"
    )
    if case.irc_nick:
        message += f"   IRC Nickname: {case.irc_nick}\n"
    if case.closed_to:
        message += f"   Case Closed To: {case.closed_to}\n"  # TODO: Translate to Seal Name (#333)
    elif case.planet:
        message += (
            f"KF Details:\n"
            f"   Planet: {case.planet}\n"
            f"   Coordinates: {case.pcoords}\n"
            f"   Case Type: {case.kftype}\n"
        )
    elif case.can_synth:
        message += (
            f"Code Black Details:\n"
            f"   Hull Remaining: {case.hull_percent}\n"
            f"   Canopy Status: {'Broken' if case.canopy_broken else 'Intact'}\n"
            f"   O2 Reported Time: {case.o2_timer}\n"
            f"   Synths Available: {'Yes' if case.can_synth else 'No'}\n"
        )
    else:
        message += f"Case Details:\n" f"   Hull Remaining: {case.hull_percent}\n"
    message += (
        f"Responder Details:\n"
        f"   Dispatchers: {', '.join(case.dispatchers) if case.dispatchers else 'None Yet!'}\n"
        f"   Responders: {', '.join(case.responders) if case.responders else 'None Yet!'}\n"
        f"   Notes: {case.case_notes if case.case_notes else 'None Yet!'}"
    )
    return message


async def create_case(args: Dict, codemap: Platform, client: HalpyBOT) -> int:
    """Create a Case on the board from a rescue announcement"""
    # Determine if an IRCN is needed by default
    ircn = re.search("/[^a-zA-Z0-9]/", args["CMDR"])
    if ircn:
        ircn = re.sub("/[^a-zA-Z0-9]/", "", args["CMDR"])
    # Create the base case
    newcase: Case = await client.board.add_case(
        client=args["CMDR"], platform=codemap, system=args["System"]
    )
    async with client.board.mod_case(newcase) as case:
        if ircn:
            case.irc_nick = ircn
        if "CanSynth" in args:
            case.hull_percent = int(args["Hull"])
            case.canopy_broken = True
            case.can_synth = True
            case.o2_timer = args["Oxygen"]
        elif "Coords" in args:
            case.planet = args["Planet"]
            case.pcoords = args["Coords"]
            case.kftype = args["KFType"]
        else:
            case.hull_percent = int(args["Hull"])
    return newcase.board_id
