"""
HalpyBOT v1.2.2

facts.py - Database interaction for the fact module

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


import mysql.connector
import logging
import src.packages.command.commandhandler
import json
from . import DatabaseConnection, NoDatabaseConnection

async def whois(subject):
    get_query = (
                f"SELECT seal_ID, COUNT(DISTINCT c.case_ID) AS cases, GROUP_CONCAT(DISTINCT CONCAT(ss.seal_name, ', ', "
                f"pl.platform_name) SEPARATOR '; '), DATE(join_date), IF(seal_ID<382, TRUE, FALSE) AS DW2Seal "
                " FROM records.cases AS c"
                " INNER JOIN records.case_assigned AS ca ON ca.case_ID = c.case_ID"
                " RIGHT JOIN sealsudb.staff as ss ON ss.seal_ID = ca.seal_kf_id"
                " INNER JOIN lookups.platform_lu AS pl ON pl.platform_id = ss.platform"
                " INNER JOIN pydle.view_joindate AS au ON au.id = ss.seal_ID"
                " INNER JOIN pydle.view_irccore AS nc ON nc.id = ss.seal_ID"
                " INNER JOIN pydle.view_ircnames AS na ON na.nc = nc.display"
                " WHERE nick = '" + subject + "';")
    try:
        db = DatabaseConnection()
        cursor = db.cursor
        cursor.execute(get_query)
        for res in cursor.fetchall():
            uID = str(res[0])
            uCases = str(res[1])
            uName = str(res[2])
            uRegdate = str(res[3])
            uDW = res[4]
            if uDW == 1:
                uDW2 = ", is a DW2 Veteran and Founder Seal with registered CMDRs of "
            else:
                uDW2 = ", with registered CMDRs of "
        db.close()
        if uID == "None":
            return ("No registered user found by that name!")
        else:
            return ("CMDR " + subject + " has a Seal ID of " + uID + ", registered on " + uRegdate + uDW2 + uName +
                         ", and has been involved with " + uCases + " rescues.")
    except mysql.connector.errors.InterfaceError:
        return "SQL injection detected! Reporting and Failing..."
    except NoDatabaseConnection:
        return "Error searching user. (0x6462636f6e6661696c)"