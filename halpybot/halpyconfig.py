"""
halpyconfig.py - Configuration Manager

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from pathlib import Path
from typing import List, Set, Optional, Union, Tuple, ClassVar
import boto3
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


class MysqlDsn(AnyUrl):
    """MySQL Scheme Config"""

    allowed_schemes = {"mysql+mysqldb"}

    @staticmethod
    def get_default_parts(parts):
        """Set the MySQL Default Port"""
        return {
            "port": "3306",
        }


class SaslBase(BaseModel):
    """SASL Identity Config"""

    identity: str


class SaslPlain(SaslBase):
    """SASL Plain Login Config"""

    username: str
    password: SecretStr


class SaslExternal(SaslBase):
    """SASL External Login Config"""

    cert: FilePath


class Irc(BaseModel):
    """IRC Server Base Settings Config"""

    server: stricturl(allowed_schemes=["irc"])
    use_ssl: bool
    nickname: str
    command_prefix: str = "!"
    operline: Optional[str] = None
    operline_password: Optional[SecretStr] = None
    sasl: Union[SaslExternal, SaslPlain]
    tls_verify: bool = False


class ApiConnector(BaseModel):
    """API Link Config"""

    port: int = 8080
    key: SecretStr
    key_check_constant: SecretStr


class Channels(BaseModel):
    """Channel List Config"""

    channel_list: List[str]


class Database(BaseModel):
    """Database Link Config"""

    connection_string: MysqlDsn
    database: str = "pydle"
    timeout: int = 10


class ForcedJoin(BaseModel):
    """Force Join Channel Config"""

    joinable: Set[str]


class OfflineMode(BaseModel):
    """Offline Mode Config"""

    enabled: bool = False
    announce_channels: List[str] = ["#bot-test"]
    warning_override: bool = False


class Edsm(BaseModel):
    """EDSM Config"""

    maximum_landmark_distance: int = 10_000
    time_cached: int = 300
    uri: AnyHttpUrl = "https://www.edsm.net"

    @property
    def system_endpoint(self) -> str:
        """System Endpoint URL"""
        return f"{self.uri}/api-v1/system"

    @property
    def systems_endpoint(self) -> str:
        """Systems Endpoint URL"""
        return f"{self.uri}/api-v1/systems"

    @property
    def sphere_endpoint(self) -> str:
        """Sphere Endpoint URL"""
        return f"{self.uri}/api-v1/sphere-systems"

    @property
    def getpos_endpoint(self) -> str:
        """Position Endpoint URL"""
        return f"{self.uri}/api-logs-v1/get-position"


class Logging(BaseModel):
    """Logging Config"""

    cli_level: str = "DEBUG"
    file_level: str = "INFO"
    log_file: FilePath = Path("logs/halpybot.log")


class DiscordNotifications(BaseModel):
    """Discord Notification Config"""

    enabled: bool = False
    webhook_id: Optional[str] = None
    webhook_token: Optional[SecretStr] = None
    case_notify: Optional[constr(regex=r"<@&(\d+)>")] = None
    trained_role: Optional[constr(regex=r"<@&(\d+)>")] = None


class Notify(BaseModel):
    """AWS SNS Notification Config"""

    enabled: bool = False
    staff: Optional[str] = None
    cybers: Optional[str] = None
    region: Optional[str] = None
    access: Optional[str] = None
    secret: Optional[SecretStr] = None
    timer: int = 5  # minutes
    WHITELIST_GROUPS: ClassVar[Tuple[str, ...]] = ("staff", "cybers")

    @property
    def sns(self) -> boto3.client:
        """SNS Catch - If Set, Enable"""
        if not (self.secret and self.access):
            return None
        return boto3.client(
            "sns",
            region_name=self.region,  # AWS Region.
            aws_access_key_id=self.access,  # AWS IAM Access Key
            aws_secret_access_key=self.secret.get_secret_value(),  # AWS IAM Secret
        )


class Facts(BaseModel):
    """Fact Table Location Config"""

    table: str = "facts"


class ManualCase(BaseModel):
    """Manual Case Send List Config"""

    send_to: List[str] = ["#seal-bob", "#Repair-Requests"]


class Twitter(BaseModel):
    """Twitter Linkup Config"""

    enabled: bool = False
    api_key: Optional[SecretStr] = None
    api_secret: Optional[SecretStr] = None
    access_token: Optional[str] = None
    access_secret: Optional[SecretStr] = None


FAILURE_BUTTON_PATH = Path.home() / ".halpy_failure_button"


class SystemMonitoring(BaseModel):
    """System Monitoring Config"""

    @property
    def failure_button(self) -> bool:
        """Failure Button Check"""
        return FAILURE_BUTTON_PATH.exists()

    @failure_button.setter
    def failure_button(self, value: bool):
        # indepmotent.
        if value:
            FAILURE_BUTTON_PATH.touch(exist_ok=True)
        else:
            FAILURE_BUTTON_PATH.unlink(missing_ok=True)


class UserAgent(BaseModel):
    """Web UserAgent Config"""

    agent_comment: str


class Yourls(BaseModel):
    """YOURLS Linkup Config"""

    uri: AnyHttpUrl
    pwd: SecretStr


class HalpyConfig(BaseSettings):
    """HalpyBOT Configuration Main"""

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

    class Config:
        """Environment/Config File Config"""

        env_file = ".env"
        env_nested_delimiter = "::"
