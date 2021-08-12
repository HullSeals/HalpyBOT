"""
HalpyBOT v1.4.2

Simple tool for automatically updating the backup fact file

WARNING: Run this tool from the halpybot/ folder, not halpybot/CLI

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import json

from src.packages.database import DatabaseConnection

jsonpath = "data/facts/backup_facts.json"

# noinspection PyBroadException
def run():
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
        with DatabaseConnection() as db:
            print("40% Connection started...")
            cursor = db.cursor()
            cursor.execute(f"SELECT factName, factLang, factText "
                           f"FROM {table}")
            print("60% Got data, parsing...")
            for (Name, Lang, Text) in cursor:
                resdict[f"{Name}-{Lang}"] = Text
        print("80% Writing to file...")
        with open(jsonpath, "w+") as jsonfile:
            json.dump(resdict, jsonfile, indent=4)
            print("100% Done. Confirm that the update was successful, and have a great day!")
    except Exception as ex:
        print("Caught an exception, aborting...")
        print(ex)


if __name__ == '__main__':
    run()
