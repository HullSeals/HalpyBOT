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
# @pytest.fixture(autouse=True)
# def _fudged_db_fx(monkeypatch):
#     """Add our test database values"""
#     from halpybot.packages import database
#     monkeypatch.setitem(database.dbconfig, "user", "root")
#     monkeypatch.setitem(database.dbconfig, "password", "passw0rd!")
#     monkeypatch.setitem(database.dbconfig, "database", "test")
#     monkeypatch.setitem(database.dbconfig, "connect_timeout", 10)
#     monkeypatch.setitem(database.dbconfig, "host", "127.0.0.1")
import pytest
from tests.mock_halpy import TestBot

@pytest.fixture()
def bot_fx():
    test_bot = TestBot(nickname="HalpyTest[BOT]")
    return test_bot
