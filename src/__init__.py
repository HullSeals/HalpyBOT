from src.packages.configmanager import config

__version__ = "1.5.2"

DEFAULT_USER_AGENT = config['UserAgent']['agent_value'] + "/" + __version__ + " " + config['UserAgent']['agent_comment']
