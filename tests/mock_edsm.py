# """
# HalpyBOT v1.6
#
# mock_edsm.py - Elite: Dangerous Star Map API interface mock instance
# Taking the call so we don't have to ping EDSM. Yay voicemail!
#
# Copyright (c) 2022 The Hull Seals,
# All rights reserved.
#
# Licensed under the GNU General Public License
# See license.md
#
# NOTE: For these tests, it is advised to run pytest with the -W ignore::DeprecationWarning due to framework issues.
# """
#
# import pytest
# from pytest_httpserver import HTTPServer
#
#
# @pytest.fixture(scope="session")
# def mock_system_api_server_fx():
#     """
#     Returns a mock HTTP server with pre-built data resembling the Fuel Rats Systems API.
#     """
#     # pylint: disable=line-too-long
#
#     with HTTPServer('127.0.0.1', '4000') as httpserver:
#         httpserver.expect_request("/api-logs-v1/system", query_string="commanderName=Rixxan&showCoordinates=1").respond_with_data(
#             """{"msgnum":100,"msg":"OK","system":"Pleiades Sector HR-W d1-79","firstDiscover":false,"date":"2022-03-15 20:51:01","coordinates":{"x":-80.625,"y":-146.65625,"z":-343.25},"isDocked":true,"station":"The Penitent","dateDocked":"2022-03-23 01:01:01","shipId":21,"shipType":"Krait MkII","shipFuel":null,"dateLastActivity":"2022-03-23 01:01:27","url":"https:\/\/www.edsm.net\/en\/user\/profile\/id\/58048\/cmdr\/Rixxan"}"""
#         )
#         httpserver.expect_request("/api-v1/system", query_string="systemName=Sol&showCoordinates=1&showInformation=1").respond_with_data(
#             """{"name":"Sol","coords":{"x":0,"y":0,"z":0},"coordsLocked":true,"information":{"allegiance":"Federation","government":"Democracy","faction":"Mother Gaia","factionState":"None","population":22780919531,"security":"High","economy":"Refinery","secondEconomy":"Service","reserve":"Common"}}"""
#         )
#         httpserver.expect_request("/api-v1/system", query_string="systemName=Praisehalpydamnwhyisthisnotasysnam&showCoordinates=1&showInformation=1").respond_with_data(
#             """[]"""
#         )
#
#         yield httpserver
