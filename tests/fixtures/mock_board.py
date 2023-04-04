"""
mock_board.py - Case Board mock instance
Loading Fake Case Data

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
from halpybot.packages.models import Platform, Case, CaseType


async def mock_full_board_fx(bot_fx):
    bot_fx.board._cases_by_id = {
        1: Case(
            board_id=1,
            client_name="one",
            platform=Platform.ODYSSEY,
            system="Delkar",
            case_type=CaseType.BLUE,
        ),
        2: Case(
            board_id=2,
            client_name="two",
            platform=Platform.XBOX,
            system="Delkar",
            case_type=CaseType.BLACK,
        ),
        3: Case(
            board_id=3,
            client_name="three",
            platform=Platform.PLAYSTATION,
            system="Delkar",
            case_type=CaseType.FISH,
        ),
        4: Case(
            board_id=4,
            client_name="four",
            platform=Platform.LIVE_HORIZONS,
            system="Delkar",
            case_type=CaseType.SEAL,
        ),
        5: Case(
            board_id=5,
            client_name="five",
            platform=Platform.LEGACY_HORIZONS,
            system="Delkar",
            case_type=CaseType.BLUE,
        ),
        6: Case(
            board_id=6,
            client_name="six",
            platform=Platform.LEGACY_HORIZONS,
            system="Delkar",
            case_type=CaseType.BLACK,
        ),
        7: Case(
            board_id=7,
            client_name="seven",
            platform=Platform.LIVE_HORIZONS,
            system="Delkar",
            case_type=CaseType.FISH,
        ),
        8: Case(
            board_id=8,
            client_name="eight",
            platform=Platform.PLAYSTATION,
            system="Delkar",
            case_type=CaseType.SEAL,
        ),
        9: Case(
            board_id=9,
            client_name="nine",
            platform=Platform.ODYSSEY,
            system="Delkar",
            case_type=CaseType.BLUE,
        ),
    }
    bot_fx.board._case_alias_name = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
    }
