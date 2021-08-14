"""
HalpyBOT v1.4.2

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

from ..configmanager import config_write, config

dbconfig = {"user": config['Database']['user'],
            "password": config['Database']['password'],
            "host": config['Database']['host'],
            "database": config['Database']['database'],
            "connect_timeout": int(config['Database']['timeout']),
            }

om_channels = [entry.strip() for entry in config.get('Offline Mode', 'announce_channels').split(',')]

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
        if config.getboolean('Offline Mode', 'Enabled'):
            raise NoDatabaseConnection
        for _ in range(3):
            # Attempt to connect to the DB
            try:
                super().__init__(**dbconfig)
                self.autocommit = autocommit
                logging.info("Connection established.")
                break
            except mysql.connector.Error as er:
                logging.error(f"Unable to connect to DB, attempting a reconnect: {er}")
                # And we do the same for when the connection fails
                if _ == 2:
                    logging.error("ABORTING CONNECTION - CONTINUING IN OFFLINE MODE")
                    # Set offline mode, can only be removed by restart
                    config_write('Offline Mode', 'enabled', 'True')
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
    try:
        db = DatabaseConnection()
        cursor = db.cursor()
        cursor.execute(get_query)
        db.close()
    except NoDatabaseConnection:
        raise
    end = time.time()
    return end
