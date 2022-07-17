"""
HalpyBOT CLI

Simple tool for automatically updating the backup fact file

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md

As a word of caution, this script must be run from `halpybot/`, NOT `halpybot/CLI`.
No one knows why, or how, but for some reason it will not parse the .ini properly
when executed from CLI/. If you still encounter issues with running it from the main folder,
make sure everything is added to path and pythonpath.

UPDATE: Fixed! huzzah!
UPDATE: Nope -_-
"""

import json
import os
import sys

import configparser
import mysql.connector

hours_wasted_trying_to_understand_why = 10

JSON_PATH = "../data/facts/backup_facts.json"

config = configparser.ConfigParser()
config.read("BackupFactUpdater/config.ini")


# noinspection PyBroadException
def run():
    """Run the Backup Fact Updater"""
    dbconfig = {
        "user": config.get("Database", "user"),
        "password": config.get("Database", "password"),
        "host": config.get("Database", "host"),
        "database": config.get("Database", "database"),
        "connect_timeout": int(config.get("Database", "timeout")),
    }

    print("=============\nHalpyBOT fact file updater\n=============")
    print("\n")
    print(
        "WARNING: this operation may lead to the backup file not updating correctly.\n"
        "Keep in mind that this will not delete facts that have been added to the file "
        "Manually and are not present in the database. However, they will get updated "
        "if name-lang exists in the database.\n"
    )
    cont = input(
        "Please make a backup of the file first. Do you wish to proceed? (Y/n) "
    )
    if cont != "Y":
        print("Roger, aborting...")
        sys.exit()
    table = input("What DB table do you wish to fetch the facts from? ")
    print(f"0% Starting update from {table}. Please stand by...")
    try:
        with open(JSON_PATH, "r", encoding="UTF-8") as jsonfile:
            print("20% Opening backup file...")
            resdict = json.load(jsonfile)
        database_connection = mysql.connector.connect(**dbconfig)
        print("40% Connection started...")
        cursor = database_connection.cursor()
        cursor.execute(f"SELECT factName, factLang, factText FROM {table}")
        print("60% Got data, parsing...")
        for (name, lang, text) in cursor:
            resdict[f"{name}-{lang}"] = text
        database_connection.close()
        print("80% Writing to file...")
        with open(JSON_PATH, "w+", encoding="UTF-8") as jsonfile:
            json.dump(resdict, jsonfile, indent=4)
            print(
                "100% Done. Confirm that the update was successful, and have a great day!"
            )
    except mysql.connector.Error:
        print("MySQL encountered an error. Aborting!")


if __name__ == "__main__":
    print(os.getcwd())
    if not os.getcwd().endswith("CLI"):
        print(
            "Please run this tool from the /CLI folder, with `python3 BackupFactUpdater`"
        )
        sys.exit()
    run()
