"""
connection.py - Database connection initialization script

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time
from sqlalchemy import create_engine, text, engine, exc
from loguru import logger
from ..configmanager import config_write, config

# dbconfig = f'mysql+mysqldb://{config["Database"]["user"]}:{config["Database"]["password"]}@127.0.0.1/{config["Database"]["database"]}'
dbconfig = f'mysql+mysqldb://{config["Database"]["user"]}:{config["Database"]["password"]}@{config["Database"]["host"]}/{config["Database"]["database"]}'

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


async def latency():
    """Ping the database and get latency
    Returns:
        Database connection latency
    """
    with engine.connect() as conn:
        get_query = "SELECT 'latency';"
        result = conn.execute(text(get_query))
    print(result)
    end = time.time()
    return end


async def box_of_angry_bees():
    if config.getboolean("Offline Mode", "Enabled"):
        raise NoDatabaseConnection
    for attempt in range(3):
        logger.info("Attempting DB Connection")
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT '1';"))
                return result
        except exc.OperationalError:
            pass
    else:
        config_write("Offline Mode", "enabled", "True")
        raise NoDatabaseConnection


# TODO:
#  1) Apply new SQLAlchemy DB Logic && REQUIRE.DATABASE to all commands
# 2) Make Async
# 3) Remove All Old Logic
# 4) Should we use sqlalchemy Session Manager here? How Best Apply New Logic?
# 5) ORM mapping logic? (TBD need based complexity)
