from requests import utils
from src.packages.configmanager import config

__version__ = "1.5-dev"

DEFAULT_USER_AGENT = config['UserAgent']['agent_value'] + "/" + __version__ + " " + config['UserAgent']['agent_comment']
utils.default_user_agent = lambda: DEFAULT_USER_AGENT
