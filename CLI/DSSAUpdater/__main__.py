"""
HalpyBOT CLI

DSSA spreadsheet scraper

Spreadsheet data used with permission from Fleetcomm and
DSSA administration

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""
import os.path
import sys
from datetime import datetime
import json
import configparser
import pyperclip
from tqdm import tqdm

from src import DSSACarrier, scrape_spreadsheet

config = configparser.ConfigParser()
config.read("DSSAUpdater/config.ini")

SHEET_LINK = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-"
    "1vTevQUcLThqo4emXE4nowJeasI07gFio4fETwevAXKIA18NhlDzbnZzRMVUOAT26OROfHG7fCXvTLgY/pubhtml?gid=0&single=true"
)

timestamp = datetime.now().strftime("%m%d%Y-%H%M%S")

# noinspection PyBroadException


def run():
    """Run the DSSA Updater"""
    print(
        "=" * 20
        + "\nCopyright (c) 2022 The Hull Seals\nDSSA file updater for HalpyBOT\n"
        + "=" * 20
        + "\n"
    )
    print(
        f"JSON and CSV files will be placed in folder: {config['Standalone']['path']}"
    )

    carriers_good = []
    carriers_bad = []
    needs_manual = []

    # Get data from the scraper
    try:
        carrierdata, issues = scrape_spreadsheet(
            path=config["Standalone"]["path"], sheetlink=SHEET_LINK, timestamp=timestamp
        )
    except FileNotFoundError:
        print(
            "Error: This isn't a directory I can access, are you running a relative dir?"
        )
        sys.exit()
    except Exception:
        print(
            f"Oops, that was an error: {Exception}. Contact Rik if the issue persists"
        )
        sys.exit()

    # Make sure we are committed to throwing 90+ queries at EDSM
    edsm_confirm = input(
        "\nEDSM querying is about to start, do you wish to proceed? (Y/n) "
    )
    if edsm_confirm.upper() != "Y":
        print(
            "Aborted. Carrrier info- and CSV files have already been created, don't forget to delete them!"
        )
        print("---")
        sys.exit()
    print("Querying from EDSM, use Ctrl+C to interrupt\n")

    # Create an object for all our carriers and get their locations
    try:
        for carrier in tqdm(carrierdata):
            crobj = DSSACarrier(name=carrier["Name"], location=carrier["Location"])
            if not crobj.has_system:
                needs_manual.append(crobj.name)
                carriers_bad.append(
                    {
                        "name": f"{crobj.location} ({crobj.name})",
                        "coords": crobj.coordinates,
                    }
                )
            else:
                carriers_good.append(
                    {
                        "name": f"{crobj.location} ({crobj.name})",
                        "coords": crobj.coordinates,
                    }
                )
    except KeyboardInterrupt:
        print(
            "\nAborted. Carrrier info- and CSV files have already been created, don't forget to delete them!"
        )
        print("---")
        sys.exit()
    except Exception:
        print(f"Uh oh, something went wrong while receiving EDSM data: {Exception}")

    # Write it to the file
    carriers = (
        carriers_good + carriers_bad
    )  # This ensures that the carriers with no coordinates will be printed last
    with open(
        f"{config['Standalone']['path']}/COORDINATES_{timestamp}.json",
        "w+",
        encoding="UTF-8",
    ) as jsonfile:
        json.dump(carriers, jsonfile, indent=4)

    # Exit
    if len(needs_manual) == 0:
        print(
            "\nDone. All carrier locations could be found in EDSM, no manual review is required"
        )
    else:
        print("\n Done. The following carriers need a manual review:\n")
        for carrier in needs_manual:
            print(f"* {carrier}")
        copydo = input("\nDo you wish to copy these names to your clipboard? (Y/n) ")
        if copydo.upper() == "Y":
            pyperclip.copy(", ".join(needs_manual))
            print("Copied.")
    print("\nUpdate completed, have a nice day.")
    print("---")
    sys.exit()


if __name__ == "__main__":
    # Tool may not be run from any other folder than CLI/ see CLI/BackupFactUpdater/__main__.py
    if not os.getcwd().endswith("CLI"):
        print("Please run this tool from the /CLI folder, with `python3 DSSAUpdater`")
        sys.exit()
    try:
        run()
    except KeyboardInterrupt:
        sys.exit()
