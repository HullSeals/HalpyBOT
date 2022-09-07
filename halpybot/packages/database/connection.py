"""
connection.py - Database connection initialization script

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time

import sqlalchemy.engine
from sqlalchemy import create_engine, text, engine, exc
import mysql.connector
from loguru import logger
from ..configmanager import config_write, config

dbconfig = f'mysql+mysqldb://{config["Database"]["user"]}:{config["Database"]["password"]}@127.0.0.1/{config["Database"]["database"]}'
# dbconfig = f'mysql+mysqldb://{config["Database"]["user"]}:{config["Database"]["password"]}@{config["Database"]["host"]}/{config["Database"]["database"]}'

engine = create_engine(
    dbconfig,
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": int(config["Database"]["timeout"])},
)

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


class DatabaseConnection(mysql.connector.MySQLConnection):
    """Governing the connection to the database"""

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
            except mysql.connector.Error as mysql_error:
                logger.exception("Unable to connect to DB, attempting a reconnect.")
                # And we do the same for when the connection fails
                if _ == 2:
                    logger.error("ABORTING CONNECTION - CONTINUING IN OFFLINE MODE")
                    # Set offline mode, can only be removed by restart
                    config_write("Offline Mode", "enabled", "True")
                    raise NoDatabaseConnection from mysql_error
                continue


async def latency():
    """Ping the database and get latency

    Returns:
        Database connection latency

    """
    try:
        with engine.connect() as conn:
            get_query = "SELECT 'latency';"
            result = conn.execute(text(get_query))
    except exc.OperationalError:
        raise NoDatabaseConnection
    print(result)
    end = time.time()
    return end
