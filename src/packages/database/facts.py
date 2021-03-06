"""
HalpyBOT v1.2

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
from . import DatabaseConnection

facts = {}

fact_index = []
basic_facts = []


async def on_connect():
    await get_facts()

async def clear_facts():
    facts.clear()
    fact_index.clear()
    basic_facts.clear()

async def update_fact_index():
    global fact_index
    factnames = facts.keys()
    for name in factnames:
        if name in fact_index:
            continue
        if "_no_args" in name:
            continue
        else:
            fact_index.append(str(name))
            if "-" not in name and name not in basic_facts:
                basic_facts.append(str(name))


async def add_fact(ctx, factname: str, facttext: str):
    db = DatabaseConnection()
    # Check if not already a command
    if factname in src.packages.command.commandhandler.Commands.commandList:
        return await ctx.reply("Cannot register fact: already an existing command!")
    # Check if fact doesn't already exist
    if factname in fact_index:
        return await ctx.reply("That fact already exists!")
    add_query = (f"INSERT INTO facts (FactName, FactText, FactAuthor) "
                 f"VALUES (%s, %s, %s);")
    add_data = (str(factname), str(facttext), str(ctx.sender))
    # FIXME quickfix
    if not hasattr(db, "cnx"):
        return await ctx.reply("Cannot add fact: bot running in offline mode.")
    try:
        cnx = db.cnx
        cursor = db.cursor
        cursor.execute(add_query, add_data)
        cnx.commit()
        logging.info(f"FACT ADDED {factname} by {ctx.sender}")
        # After fact is added to DB, update cache
        await clear_facts()
        await get_facts()
        await update_fact_index()
        await ctx.reply("Fact added successfully")
    except mysql.connector.Error as er:
        print(f"ERROR in registering fact {factname} by {ctx.sender}: {er}")
        return await ctx.reply("Couldn't add fact! contact a cyber")
    finally:
        db.close()

async def remove_fact(ctx, factname: str):
    db = DatabaseConnection()
    # Check if fact exists
    if factname not in fact_index:
        return await ctx.reply("That fact doesn't exist!")
    remove_query = (f"DELETE FROM facts "
                    f"WHERE factName = %s;")
    remove_data = (str(factname),)
    # FIXME quickfix
    if not hasattr(db, "cnx"):
        return await ctx.reply("Cannot remove fact: bot running in offline mode.")
    try:
        cnx = db.cnx
        cursor = db.cursor
        cursor.execute(remove_query, remove_data)
        cnx.commit()
        logging.info(f"FACT REMOVED {factname} by {ctx.sender}")
        # After fact is removed from DB, update cache
        await clear_facts()
        await get_facts()
        await update_fact_index()
        await ctx.reply("Fact removed successfully.")
    except mysql.connector.Error as er:
        print(f"ERROR in deleting fact {factname} by {ctx.sender}: {er}")
        return await ctx.reply("Couldn't delete fact! contact a cyber")
    finally:
        db.close()


async def get_facts():
    db = DatabaseConnection()
    get_query = (f"SELECT factName, factText "
                 f"FROM facts")
    # FIXME quickfix
    if not hasattr(db, "cnx"):
        # Get facts from the backup file if we have no connection
        logging.error("ERROR in getting facts from DB")
        global facts
        with open('src/facts/backup_facts.json') as json_file:
            facts = json.load(json_file)
        return await update_fact_index()
    cursor = db.cursor
    cursor.execute(get_query)
    for (factName, factText) in cursor:
        facts[str(factName)] = factText
    await update_fact_index()
    db.close()
