"""
HalpyBOT v1.6

mock_edsm.py - Elite: Dangerous Star Map API interface mock instance
Taking the call so we don't have to ping EDSM. Yay voicemail!

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import pytest
from pytest_httpserver import HTTPServer


@pytest.fixture(scope="session", autouse=True)
def mock_api_server_fx():
    """
    Returns a mock HTTP server with pre-built data resembling the EDSM API.
    """
    with HTTPServer("127.0.0.1", "4000") as mock:
        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=SOL&showCoordinates=1&showInformation=1",
        ).respond_with_json(
            {
                "name": "Sol",
                "coords": {"x": 0, "y": 0, "z": 0},
                "coordsLocked": "true",
                "information": {
                    "allegiance": "Federation",
                    "government": "Democracy",
                    "faction": "Mother Gaia",
                    "factionState": "None",
                    "population": 22780919531,
                    "security": "High",
                    "economy": "Refinery",
                    "secondEconomy": "Service",
                    "reserve": "Common",
                },
            }
        )
        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=PRAISEHALPYDAMNWHYISTHISNOTASYSNAM&showCoordinates=1&showInformation=1",
        ).respond_with_json([])
        mock.expect_request(
            "/api-v1/sphere-systems", query_string="x=1&y=2&z=3&radius=100&minRadius=1"
        ).respond_with_json(
            [
                {"distance": 98.25, "bodyCount": 9, "name": "Hixkar"},
                {"distance": 98.72, "bodyCount": 2, "name": "Cephei Sector RD-T b3-2"},
                {
                    "distance": 99.25,
                    "bodyCount": 22,
                    "name": "Col 285 Sector IT-W b16-3",
                },
                {"distance": 97.58, "bodyCount": 19, "name": "Taurawa"},
                {
                    "distance": 99.45,
                    "bodyCount": 3,
                    "name": "Col 285 Sector EN-Y b15-3",
                },
                {
                    "distance": 99.21,
                    "bodyCount": 11,
                    "name": "Col 285 Sector KE-V b17-6",
                },
                {"distance": 96.19, "bodyCount": 30, "name": "Herlio"},
                {"distance": 97.15, "bodyCount": 34, "name": "Soma"},
                {"distance": 99.88, "bodyCount": 2, "name": "Enete"},
                {"distance": 99.18, "bodyCount": 18, "name": "Jieguaje"},
                {"distance": 94.71, "bodyCount": 44, "name": "Karini"},
                {"distance": 98.8, "bodyCount": 29, "name": "BD+49 3937"},
                {
                    "distance": 95.47,
                    "bodyCount": 4,
                    "name": "Col 285 Sector DM-L c8-19",
                },
                {"distance": 95.22, "bodyCount": 20, "name": "LTT 16301"},
                {"distance": 99.4, "bodyCount": 18, "name": "Djedet"},
            ]
        )
        mock.expect_request(
            "/api-v1/sphere-systems",
            query_string="x=1000000000&y=20000000000&z=30000000000&radius=100&minRadius=1",
        ).respond_with_json([])
        mock.expect_request(
            "/api-logs-v1/get-position",
            query_string="commanderName=Rixxan&showCoordinates=1",
        ).respond_with_json(
            {
                "msgnum": 100,
                "msg": "OK",
                "system": "Pleiades Sector HR-W d1-79",
                "firstDiscover": "false",
                "date": "2022-03-15 20:51:01",
                "coordinates": {"x": -80.625, "y": -146.65625, "z": -343.25},
                "isDocked": "true",
                "station": "The Penitent",
                "dateDocked": "2022-03-23 01:01:01",
                "shipId": 21,
                "shipType": "Krait MkII",
                "shipFuel": "null",
                "dateLastActivity": "2022-03-23 01:01:27",
                "url": "https://www.edsm.net/en/user/profile/id/58048/cmdr/Rixxan",
            }
        )
        mock.expect_request(
            "/api-logs-v1/get-position",
            query_string="commanderName=Praisehalpydamnwhyisthisnotacmdrnam&showCoordinates=1",
        ).respond_with_json({"msgnum": 203, "msg": "Commander name/API Key not found"})
        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=DELKAR&showCoordinates=1&showInformation=1",
        ).respond_with_json(
            {
                "name": "Delkar",
                "coords": {"x": 67.8125, "y": 32.65625, "z": 35.25},
                "coordsLocked": "true",
                "information": {
                    "allegiance": "Federation",
                    "government": "Corporate",
                    "faction": "Federal Reclamation Co",
                    "factionState": "Boom",
                    "population": 283812,
                    "security": "Medium",
                    "economy": "Industrial",
                    "secondEconomy": "Refinery",
                    "reserve": "Pristine",
                },
            }
        )
        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=SAGITTARIUS+B*&showCoordinates=1&showInformation=1",
        ).respond_with_json([])
        mock.expect_request(
            "/api-logs-v1/get-position",
            query_string="commanderName=Sagittarius+B*&showCoordinates=1",
        ).respond_with_json({"msgnum": 203, "msg": "Commander name/API Key not found"})
        mock.expect_request(
            "/api-logs-v1/get-position",
            query_string="commanderName=SAGITTARIUS+B*&showCoordinates=1",
        ).respond_with_json({"msgnum": 203, "msg": "Commander name/API Key not found"})

        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=COL+285+SECTOR+AA-A+A30-2&showCoordinates=1&showInformation=1",
        ).respond_with_json(
            {
                "name": "Col 285 Sector AA-A a30-2",
                "coords": {"x": 104.65625, "y": -35.09375, "z": -33.8125},
                "coordsLocked": "true",
                "information": {},
            }
        )
        mock.expect_request(
            "/api-v1/systems", query_string="systemName=SAGITTARIUS+A*"
        ).respond_with_json([{"name": "Sagittarius A*"}])
        mock.expect_request(
            "/api-v1/systems", query_string="systemName=DELKAR+3+A"
        ).respond_with_json([])
        mock.expect_request(
            "/api-v1/systems", query_string="systemName=DELKAR+3"
        ).respond_with_json([])
        mock.expect_request(
            "/api-v1/systems", query_string="systemName=DELKAR"
        ).respond_with_json([{"name": "Delkar"}])
        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=SAGITTARIUS+A*&showCoordinates=1&showInformation=1",
        ).respond_with_json(
            {
                "name": "Sagittarius A*",
                "coords": {"x": 25.21875, "y": -20.90625, "z": 25899.96875},
                "coordsLocked": "true",
                "information": {},
            }
        )
        mock.expect_request(
            "/api-logs-v1/get-position",
            query_string="commanderName=ThisCMDRDoesntExist&showCoordinates=1",
        ).respond_with_json({"msgnum": 203, "msg": "Commander name/API Key not found"})
        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=THISCMDRDOESNTEXIST&showCoordinates=1&showInformation=1",
        ).respond_with_json([])
        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=RIXXAN&showCoordinates=1&showInformation=1",
        ).respond_with_json([])
        mock.expect_request(
            "/api-v1/system",
            query_string="systemName=SKAUDOAE+UF-Q+B47-1&showCoordinates=1&showInformation=1",
        ).respond_with_json(
            {
                "name": "Skaudoae UF-Q b47-1",
                "coords": {"x": -1700.5, "y": -1081, "z": 10195.53125},
                "coordsLocked": "false",
                "information": {},
            }
        )
        yield HTTPServer
