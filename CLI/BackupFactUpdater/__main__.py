"""
HalpyBOT CLI

Simple tool for automatically updating the backup fact file

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import json
import os

import mysql.connector
import configparser

"""
As a word of caution, this script must be run from `halpybot/`, NOT `halpybot/CLI`.
No one knows why, or how, but for some reason it will not parse the .ini properly
when executed from CLI/. If you still encounter issues with running it from the main folder,
make sure everything is added to path and pythonpath.

UPDATE: Fixed! huzzah!
UPDATE: Nope -_-
"""

hours_wasted_trying_to_understand_why = 10

jsonpath = "data/facts/backup_facts.json"

config = configparser.ConfigParser()
config.read('BackupFactUpdater/config.ini')


# noinspection PyBroadException
def run():

    dbconfig = {"user": config.get('Database', 'user'),
                "password": config.get('Database', 'password'),
                "host": config.get('Database', 'host'),
                "database": config.get('Database', 'database'),
                "connect_timeout": int(config.get('Database', 'timeout'))
                }

    print("=============\n"
          "HalpyBOT fact file updater\n"
          "=============")
    print("\n")
    print("WARNING: this operation may lead to the backup file not updating correctly.\n"
          "Keep in mind that this will not delete facts that have been added to the file "
          "Manually and are not present in the database. However, they will get updated "
          "if name-lang exists in the database.\n")
    cont = input("Please make a backup of the file first. Do you wish to proceed? (Y/n) ")
    if cont != "Y":
        print("Roger, aborting...")
        exit()
    table = input("What DB table do you wish to fetch the facts from? ")
    print(f"0% Starting update from {table}. Please stand by...")
    try:
        with open(jsonpath, "r") as jsonfile:
            print("20% Opening backup file...")
            resdict = json.load(jsonfile)
        DatabaseConnection = mysql.connector.connect(**dbconfig)
        print("40% Connection started...")
        cursor = DatabaseConnection.cursor()
        cursor.execute(f"SELECT factName, factLang, factText "
                       f"FROM {table}")
        print("60% Got data, parsing...")
        for (Name, Lang, Text) in cursor:
            resdict[f"{Name}-{Lang}"] = Text
        DatabaseConnection.close()
        print("80% Writing to file...")
        with open(jsonpath, "w+") as jsonfile:
            json.dump(resdict, jsonfile, indent=4)
            print("100% Done. Confirm that the update was successful, and have a great day!")
    except Exception as ex:
        print("Caught an exception, aborting...")
        print(ex)


if __name__ == '__main__':
    print(os.getcwd())
    if not os.getcwd().endswith("/CLI"):
        print("Please run this tool from the /CLI folder, with `python3 BackupFactUpdater`")
        exit()
    run()
