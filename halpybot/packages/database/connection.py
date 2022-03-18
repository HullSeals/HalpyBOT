"""
HalpyBOT v1.5.2

connection.py - Database connection initialization script

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import mysql.connector
from mysql.connector import MySQLConnection
import logging
import time
import asyncio

from ..configmanager import config_write, config


class GrafanaHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno > 40:
            asyncio.ensure_future(
                self._upload_log(record.filename, record.levelno, record.msg)
            )

    @staticmethod
    async def _upload_log(name: str, prio: int, msg: str) -> None:
        try:
            with DatabaseConnection() as db:
                cursor = db.cursor()
                cursor.callproc("spCreateHalpyErrLog", [name, prio, msg])
        except NoDatabaseConnection:
            # TODO stash DB call and execute once we get back to online mode
            pass


Grafana = GrafanaHandler()


logger = logging.getLogger(__name__)


dbconfig = {
    "user": config["Database"]["user"],
    "password": config["Database"]["password"],
    "host": config["Database"]["host"],
    "database": config["Database"]["database"],
    "connect_timeout": int(config["Database"]["timeout"]),
}

om_channels = [
    entry.strip()
    for entry in config.get("Offline Mode", "announce_channels").split(",")
]


class NoDatabaseConnection(ConnectionError):
    """
    Raised when 3 consecutive attempts at reconnection are unsuccessful
    """

    pass


class DatabaseConnection(MySQLConnection):
    def __init__(self, autocommit: bool = True):
        """Create a new database connection

        When we can't establish a connection, two more retries are attempted. If both fail,
        we enter Offline Mode.

        Raises:
            NoDatabaseConnection: Raised when 3 consecutive connection attempts are unsuccessful

        """
        if config.getboolean("Offline Mode", "Enabled"):
            raise NoDatabaseConnection
        for _ in range(3):
            # Attempt to connect to the DB
            try:
                super().__init__(**dbconfig)
                self.autocommit = autocommit
                logger.info("Connection established.")
                break
            except mysql.connector.Error as er:
                logger.error(f"Unable to connect to DB, attempting a reconnect: {er}")
                # And we do the same for when the connection fails
                if _ == 2:
                    logger.error("ABORTING CONNECTION - CONTINUING IN OFFLINE MODE")
                    # Set offline mode, can only be removed by restart
                    config_write("Offline Mode", "enabled", "True")
                    raise NoDatabaseConnection
                continue

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


async def latency():
    """Ping the database and get latency

    Returns:
        Database connection latency

    """
    get_query = "SELECT 'latency';"
    db = DatabaseConnection()
    cursor = db.cursor()
    cursor.execute(get_query)
    db.close()
    end = time.time()
    return end
