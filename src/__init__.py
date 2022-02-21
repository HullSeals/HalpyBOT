from src.packages.configmanager import config

__version__ = "1.5.2"

# Normal User Agent string follows: Product/version (<system-information>) <platform> (<platform-details>)
DEFAULT_USER_AGENT = "HalpyBOT/" + __version__ + " (" + config['IRC']['nickname'] + ") "\
                     + config['UserAgent']['agent_comment']
