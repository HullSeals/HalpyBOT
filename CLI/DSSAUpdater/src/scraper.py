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
