import warnings
from pathlib import Path
from pydantic import (
    BaseSettings,
    SecretStr,
    AnyUrl,
    BaseModel,
    stricturl,
    AnyHttpUrl,
    FilePath,
    constr,
)
from typing import List, Set, Optional, Union, Tuple

from typing import ClassVar


class MysqlDsn(AnyUrl):
    allowed_schemes = {"mysql+mysqldb"}

    @staticmethod
    def get_default_parts(parts):
        return {
            "port": "3306",
        }


class SaslBase(BaseModel):
    identity: str


class SaslPlain(SaslBase):
    username: str
    password: SecretStr


class SaslExternal(SaslBase):
    cert: FilePath


class Irc(BaseModel):
    server: stricturl(allowed_schemes=["irc"])
    use_ssl: bool
    nickname: str
    command_prefix: str = "!"
    operline: Optional[str] = None
    operline_password: Optional[SecretStr] = None
    sasl: Union[SaslExternal, SaslPlain]


class ApiConnector(BaseModel):
    port: int = 8080
    key: SecretStr
    key_check_constant: SecretStr


class Channels(BaseModel):
    channel_list: List[str]


class Database(BaseModel):
    connection_string: MysqlDsn
    timeout: int = 10


class ForcedJoin(BaseModel):
    joinable: Set[str]


class OfflineMode(BaseModel):
    enabled: bool = False
    announce_channels: List[str] = ["#bot-test"]
    warning_override: bool = False


class Edsm(BaseModel):
    maximum_landmark_distance: int = 10_000
    time_cached: int = 300
    uri: AnyHttpUrl = "https://www.edsm.net"

    @property
    def system_endpoint(self) -> str:
        return f"{self.uri}/api-v1/system"

    @property
    def systems_endpoint(self) -> str:
        return f"{self.uri}/api-v1/systems"

    @property
    def sphere_endpoint(self) -> str:
        return f"{self.uri}/api-v1/sphere-systems"

    @property
    def getpos_endpoint(self) -> str:
        return f"{self.uri}/api-logs-v1/get-position"


class Logging(BaseModel):
    cli_level: str = "DEBUG"
    file_level: str = "INFO"
    log_file: FilePath = "logs/halpybot.log"


class DiscordNotifications(BaseModel):
    webhook_id: Optional[str] = None
    webhook_token: Optional[SecretStr] = None
    case_notify: Optional[constr(regex=r"<@&(\d+)>")] = None
    trained_role: Optional[constr(regex=r"<@&(\d+)>")] = None


class Notify(BaseModel):
    staff: Optional[str] = None
    cybers: Optional[str] = None
    region: Optional[str] = None
    access: Optional[str] = None
    secret: Optional[SecretStr] = None
    timer: int = 5  # minutes
    WHITELIST_GROUPS: ClassVar[Tuple[str, ...]] = ("staff", "cybers")


class Facts(BaseModel):
    table: str = "facts"


class ManualCase(BaseModel):
    send_to: List[str] = ["#seal-bob", "#Repair-Requests"]


class Twitter(BaseModel):
    enabled: bool = False
    api_key: Optional[SecretStr] = None
    api_secret: Optional[SecretStr] = None
    access_token: Optional[str] = None
    access_secret: Optional[SecretStr] = None


FAILURE_BUTTON_PATH = Path.home() / ".halpy_failure_button"


class SystemMonitoring(BaseModel):
    enabled: bool = True
    anope_timer: int = 300
    message_channel: str = "#seal-bob"

    @property
    def failure_button(self) -> bool:
        return FAILURE_BUTTON_PATH.exists()

    @failure_button.setter
    def failure_button(self, value: bool):
        # indepmotent.
        if value:
            FAILURE_BUTTON_PATH.touch(exist_ok=True)
        else:
            FAILURE_BUTTON_PATH.unlink(missing_ok=True)


class UserAgent(BaseModel):
    agent_comment: str


class Yourls(BaseModel):
    uri: AnyHttpUrl
    pwd: SecretStr


class HalpyConfig(BaseSettings):
    irc: Irc
    api_connector: ApiConnector
    channels: Channels
    database: Optional[Database] = None
    forced_join: ForcedJoin
    offline_mode: OfflineMode = OfflineMode()
    edsm: Edsm = Edsm()
    logging: Logging = Logging()
    discord_notifications: DiscordNotifications = DiscordNotifications()
    notify: Notify = Notify()
    facts: Facts = Facts()
    manual_case: ManualCase = ManualCase()
    twitter: Twitter = Twitter()
    system_monitoring: SystemMonitoring = SystemMonitoring()
    user_agent: UserAgent
    yourls: Optional[Yourls] = None

    def write(self, *args):
        warnings.warn("This function is deprecated.", DeprecationWarning)
        raise NotImplementedError

    class Config:
        env_file = ".env"
        env_nested_delimiter = "::"
