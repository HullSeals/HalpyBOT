# import pytest
#
# @pytest.fixture(autouse=True)
# def _fudged_config_fx(monkeypatch):
#     from halpybot.packages import configmanager
#     config = {
#         'SASL': {
#             'identity': 'MySASLIdentity',
#             'username': 'MySASLIdentity',
#             'password': 'ASuperSecureP@ssword!'
#         },
#         'IRC': {
#             'server': '127.0.0.1',
#             'port': '+6697',
#             'usessl': True,
#             'nickname': 'HalpyBOT',
#             'commandPrefix': '!',
#             'operline': 'MyOperLine',
#             'operlinePassword': 'IAmMORBO!'
#         },
#         'API Connector': {
#             'port': '8080',
#             'key': 'bacon',
#             'key_check_constant': 'mayonayse'
#         },
#         'Channels': {
#             'ChannelList': '#bot-test'
#         },
#         'Database': {
#             'user': 'bob',
#             'password': 'thebuilder',
#             'host': '127.0.0.1',
#             'database': 'pydle',
#             'timeout': '10'
#         },
#         'Force join command': {
#             'joinable': '#bot-test #cybers'
#         },
#         'Offline Mode': {
#             'enabled': False,
#             'announce_channels': '#bot-test',
#             'warning_override': False
#         },
#         'EDSM': {
#             'Maximum landmark distance': '10000',
#             'timeCached': '300',
#             'uri': '127.0.0.1',
#             'system_endpoint': 'api-v1/system',
#             'systems_endpoint': 'api-v1/systems',
#             'sphere_endpoint': 'api-v1/sphere-systems',
#             'getpos_endpoint': 'api-logs-v1/get-position'
#         },
#         'Logging': {
#             'cli_level': 'DEBUG',
#             'file_level': 'INFO',
#             'log_file': 'logs/halpybot.log'
#         },
#         'Discord Notifications': {
#             'webhook_id': '8675309',
#             'webhook_token': 'PUNY_HUMAN_NUMBER_ONE',
#             'CaseNotify': '<@&123456789123456789>',
#             'TrainedRole': '<@&123456789123456789>'
#         },
#         'Notify': {
#             'staff': 'arn:aws:sns:us-east-2:12345678:CyberTest',
#             'cybers': 'arn:aws:sns:us-east-2:12345678:CyberTest',
#             'region': 'us-east-2',
#             'access': 'DENIED',
#             'secret': 'someSecretText',
#             'timer': '300'
#         },
#         'Facts': {
#             'table': 'facts'
#         },
#         'Manual Case': {
#             'send_to': '#bot-test'
#         },
#         'Twitter': {
#             'enabled': False,
#             'api_key': 'LockPickingLawyer',
#             'api_secret': 'Blargh',
#             'access_token': 'fadsjkluijkhasfdhuioyfsadjkloasfdhuiofsd',
#             'access_secret': 'asdfjklqwertyuiop'
#         },
#         'System Monitoring': {
#             'enabled': True,
#             'anope_timer': '300',
#             'message_channel': '#bot-test',
#             'failure_button': False
#         },
#         'UserAgent': {
#             'agent_comment': 'RICHARD NIXON'
#         }
#     }
#     monkeypatch.setattr(configmanager, "config", config)
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
#         httpserver.expect_request("/api-logs-v1/get-position", query_string="commanderName=Rixxan&showCoordinates=1").respond_with_data(
#             """{"msgnum":100,"msg":"OK","system":"Pleiades Sector HR-W d1-79","firstDiscover":false,"date":"2022-03-15 20:51:01","coordinates":{"x":-80.625,"y":-146.65625,"z":-343.25},"isDocked":true,"station":"The Penitent","dateDocked":"2022-03-23 01:01:01","shipId":21,"shipType":"Krait MkII","shipFuel":null,"dateLastActivity":"2022-03-23 01:01:27","url":"https:\/\/www.edsm.net\/en\/user\/profile\/id\/58048\/cmdr\/Rixxan"}"""
#         )
#
#         yield httpserver

import pytest
from pytest_httpserver import HTTPServer


@pytest.fixture(scope="session")
def mock_system_api_server_fx():
    """
    Returns a mock HTTP server with pre-built data resembling the Fuel Rats Systems API.
    """
    # pylint: disable=line-too-long

    with HTTPServer('127.0.0.1', '4000') as httpserver:
        httpserver.expect_request("/api-logs-v1/system", query_string="commanderName=Rixxan&showCoordinates=1").respond_with_data(
            """{"msgnum":100,"msg":"OK","system":"Pleiades Sector HR-W d1-79","firstDiscover":false,"date":"2022-03-15 20:51:01","coordinates":{"x":-80.625,"y":-146.65625,"z":-343.25},"isDocked":true,"station":"The Penitent","dateDocked":"2022-03-23 01:01:01","shipId":21,"shipType":"Krait MkII","shipFuel":null,"dateLastActivity":"2022-03-23 01:01:27","url":"https:\/\/www.edsm.net\/en\/user\/profile\/id\/58048\/cmdr\/Rixxan"}"""
        )
        httpserver.expect_request("/api-v1/system", query_string="systemName=Sol&showCoordinates=1&showInformation=1").respond_with_data(
            """{"name":"Sol","coords":{"x":0,"y":0,"z":0},"coordsLocked":true,"information":{"allegiance":"Federation","government":"Democracy","faction":"Mother Gaia","factionState":"None","population":22780919531,"security":"High","economy":"Refinery","secondEconomy":"Service","reserve":"Common"}}"""
        )
        httpserver.expect_request("/api-v1/system", query_string="systemName=Praisehalpydamnwhyisthisnotasysnam&showCoordinates=1&showInformation=1").respond_with_data(
            """[]"""
        )

        yield httpserver

