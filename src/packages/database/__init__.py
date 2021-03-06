"""
HalpyBOT v1.2

database\__init__.py - Database connection initialization script

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

# PyCharm tells me these imports are not used, but they are. Do not remove.
import configparser
import mysql.connector
from mysql.connector import Error as NoDatabaseConnection
import logging

from ..database import *

config = configparser.ConfigParser()
config.read('config/config.ini')

dbconfig = {"user": config['Database']['user'],
            "password": config['Database']['password'],
            "host": config['Database']['host'],
            "database": config['Database']['database']}

# Assume not in offline mode
offline_mode: bool = False

class DatabaseConnection:

    def __init__(self):
        global offline_mode
        if offline_mode is True:
            raise ConnectionError
        for _ in range(3):
            # Attempt to connect to the DB
            try:
                cnx = mysql.connector.connect(**dbconfig)
                cursor = cnx.cursor()
                cnx.autocommit = True
                self.cnx = cnx
                self.cursor = cursor
                logging.info("Connection established.")
                break
            except NoDatabaseConnection as er:
                logging.error(f"Unable to connect to DB, attempting a reconnect: {er}")
                # And we do the same for when the connection fails
                if _ == 2:
                    logging.error("ABORTING CONNECTION - CONTINUING IN OFFLINE MODE")
                    # Set offline mode, can only be removed by restart
                    offline_mode = True
                    # TODO send messages to channels
                    raise ConnectionError
                continue

    def close(self):
        self.cnx.close()
