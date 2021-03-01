"""
HalpyBOT v1.2

database\__init__.py - Database connection initialization script

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import configparser
import mysql.connector

config = configparser.ConfigParser()
config.read('config/config.ini')

dbconfig = config['Database']

try:
    cnx = mysql.connector.connect(user=dbconfig['user'],
                                  password=dbconfig['password'],
                                  host=dbconfig['host'],
                                  database=dbconfig['database'])
    print("Database connection established")
    cursor = cnx.cursor()
    cnx.autocommit = True
except mysql.connector.Error as error:
    cnx = None
    cursor = None
    print(f"Cannot connect to database, starting in offline mode: {error}")
