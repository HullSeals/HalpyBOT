"""
HalpyBOT CLI

scraper.py - Spreadsheet scraper function, powered by BeautifulSoup

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from bs4 import BeautifulSoup
import csv
import requests
import configparser
import os
from datetime import datetime

config = configparser.ConfigParser()
os.chdir("..")
config.read("config/config.ini")

class SpreadsheetLayoutError(Exception):
    """
    Some anomaly was encountered while reading the spreadsheet that prevents the
    system from functioning normally. Please confirm the correct spreadsheet is being used
    """

def scrape_spreadsheet():

    anomalies = []

    # First, we request the spreadsheet from the link and let BS do it's thing
    html = requests.get(str(config['Settings']['link'])).text
    tables = BeautifulSoup(html, "lxml").find_all("table")

    # Store the results
    if len(tables) > 1:
        raise SpreadsheetLayoutError("More than one table was found")
    rows = ([[td.text for td in row.find_all("td")] for row in tables[0].find_all("tr")])

    # If we want to output the results to a file for I-don't-know-what, do that
    if config.getboolean('Standalone', 'output_csv'):
        with open(f"{config['Standalone']['path']}/dssa_{datetime.now().strftime('%m%d%Y-%H%M%S')}.csv", "w") as f:
            wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            wr.writerows(rows)

    # Get rid of all rows we don't want to include

    usable = []
    rows = rows[3:]  # These are empty and/or useless anyway
    # Convert everything to a dictionary for easier object creation later down the line
    for index, row in enumerate(rows):
        if row == ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']:
            continue
        if row[2].lower() != 'carrier operational':
            continue
        elif row[9] == '':
            anomalies.append(f"{index+1} - Name field has no value")
        elif row[12] == '':
            anomalies.append(f"{index+1} - Location field has no value")
        else:
            usable.append(row[1:])

    # Now, we can convert these lists into dictionaries for easier reading later down the line
    carriers = []
    for row in usable:
        carriers.append({
                "ID": row[0],
                "Status": row[1],
                "Operation Name": row[2],
                "Launch Date": row[3],
                "Link": row[4],
                "Platform": row[5],
                "Distance": row[6],
                "Name": row[8],
                "Callsign": row[9],
                "Location": row[10],
                "Destination": row[11],
                "Region": row[12],
                "Owner": row[13],
                "Group": row[14],
                "Services": row[16].split(', '),
                "Donation": row[17],
                "EOL": row[18],
        })

    return carriers, anomalies
