"""
connection.py - Database connection initialization script

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import time
from loguru import logger
from sqlalchemy import create_engine, text, exc
from halpybot import config

dbconfig = f"{config.database.connection_string}/{config.database.database}"

engine = create_engine(
    dbconfig,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"connect_timeout": config.database.timeout},
)


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
        conn.execute(text("SELECT 'latency'"))
    end = time.time()
    return end


async def test_database_connection():
    """
    Test the database connection. Set offline mode if an error occurs.
    A.K.A. The artist formerly known as "Box of Angry Bees"
    """
    if config.offline_mode.enabled:
        raise NoDatabaseConnection
    attempt = 0
    for attempt in range(1, 4):
        logger.info("Attempting DB Connection")
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT '1'"))
                logger.info(f"Succeeded on attempt {attempt}")
                return
        except exc.OperationalError:
            pass
    config.offline_mode.enabled = True
    logger.info(f"Failed on attempt {attempt}")
    raise NoDatabaseConnection
