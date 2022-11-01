"""
HalpyBOT CLI

Simple tool for automatically updating the backup fact file

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import json
import sys
import pathlib
import configparser
import mysql.connector


# noinspection PyBroadException
def run():
    """Run the Backup Fact Updater"""
    rootpath = pathlib.PurePath(__file__).parent.parent.parent
    rootpath = str(rootpath).replace("\\", "/")
    print(rootpath)
    json_path = rf"{rootpath}/data/facts/backup_facts.json"
    config = configparser.ConfigParser()
    config.read(rf"{rootpath}/CLI/BackupFactUpdater/config.ini")

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
    if cont.upper() != "Y":
        print("Roger, aborting...")
        sys.exit()
    table = input("What DB table do you wish to fetch the facts from? ")
    print(f"0% Starting update from {table}. Please stand by...")
    try:
        with open(json_path, "r", encoding="UTF-8") as jsonfile:
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
        with open(json_path, "w+", encoding="UTF-8") as jsonfile:
            json.dump(resdict, jsonfile, indent=4)
            print(
                "100% Done. Confirm that the update was successful, and have a great day!"
            )
    except mysql.connector.Error:
        print("MySQL encountered an error. Aborting!")


if __name__ == "__main__":
    run()
