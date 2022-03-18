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
import json


class SpreadsheetLayoutError(Exception):
    """
    Some anomaly was encountered while reading the spreadsheet that prevents the
    system from functioning normally. Please confirm the correct spreadsheet is being used
    """


def scrape_spreadsheet(path: str, sheetlink: str, timestamp: str):
    """Scrape the DSSA spreadsheet for info

    This *will* silently break if the layout of this spreadsheet changes

    Args:
        path (str): Path the .csv and .json files are to be stored in
        sheetlink (str): Link to the Google Spreadsheet
        timestamp (str): Current time

    Returns:
        (tuple): a tuple of the list of carriers, and a list of problems
            encountered while scraping

    """

    anomalies = []

    # First, we request the spreadsheet from the link and let BS do its thing
    html = requests.get(sheetlink).text
    tables = BeautifulSoup(html, "lxml").find_all("table")

    # Store the results
    if len(tables) > 1:
        raise SpreadsheetLayoutError("More than one table was found")
    rows = [[td.text for td in row.find_all("td")] for row in tables[0].find_all("tr")]

    # Before we do anything else, cram it all into a .csv for Mr. User to do a thing with
    # NOTE: this .csv file is not used for processing the data as is happening a few lines ahead
    # it just exists for your (yes dear reader, YOU!) convenience
    with open(f"{path}/dssa_{timestamp}.csv", "w") as f:
        csv.writer(f, quoting=csv.QUOTE_NONNUMERIC).writerows(rows)
        print(f"\nRaw spreadsheet copied into: dssa_{timestamp}.csv")

    # Get rid of all rows we don't want to include
    usable = []
    rows = rows[3:]  # 0, 1 and 2 are always useless, empty, or both
    for index, row in enumerate(rows):
        if row == [""] * 20:  # This would be an empty row, ignore it
            continue
        if row[2].lower() != "carrier operational":  # 2 - Carrier status
            continue
        elif row[9] == "":  # 9 - Carrier name
            anomalies.append(f"{index + 1} - Name field has no value")
        elif row[12] == "":  # 12 - Location
            anomalies.append(f"{index + 1} - Location field has no value")
        else:
            usable.append(row[1:])

    # Now, we can convert these lists into dictionaries for easier reading later down the line
    carriers = []
    for row in usable:
        carriers.append(
            {
                "ID": row[0],
                "Status": row[1],
                "Operation Name": row[2],
                "Launch Date": row[3],
                "Link": row[4],
                "Platform": row[5],
                "Distance": row[6],  # Row 7 is skipped because it never holds any value
                "Name": row[8],
                "Callsign": row[9],
                "Location": row[10],
                "Destination": row[11],
                "Region": row[12],
                "Owner": row[13],
                "Group": row[14],  # Same with 15
                "Services": row[16].split(", "),  # Services are listed
                "Donation": row[17],
                "EOL": row[18],
            }
        )

    # And finally, create a file with all carrier info + any problems that may have arisen
    with open(f"{path}/carrier_data_{timestamp}.json", "w+") as jsonfile:
        json.dump([carriers, {"Issues": anomalies}], jsonfile, indent=4)
        print(f"Carrier data copied to: carrier_data_{timestamp}.json")

    return (
        carriers,
        anomalies,
    )  # Return the data as a dictionary, not a json file, so we don't have to unpack it
