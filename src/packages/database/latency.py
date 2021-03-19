"""
HalpyBOT v1.2.3

latency.py - Test the connection speed between the bot and the IRC DB.

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


import mysql.connector
from . import DatabaseConnection, NoDatabaseConnection
import time

async def latency():
    get_query = ("SELECT 'latency';")
    try:
        db = DatabaseConnection()
        cursor = db.cursor
        cursor.execute(get_query)
        db.close()
    except NoDatabaseConnection:
        return "Not Connected to Database. (0x6462636f6e6661696c)"
    end = time.time()
    return end
