"""
HalpyBOT v1.1

database.py - Main database interaction module

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""


import mysql.connector
import logging
import src.commandhandler
from main import config
import json

dbconfig = config['Database']

facts = {}

fact_index = []
basic_facts = []

try:
    cnx = mysql.connector.connect(user=dbconfig['user'],
                                  password=dbconfig['password'],
                                  host=dbconfig['host'],
                                  database=dbconfig['database'])
    print("Database connection established")
    cursor = cnx.cursor()
    cnx.autocommit = True
except mysql.connector.Error as error:
    cnx = None
    print(f"Cannot connect to database, starting in offline mode: {error}")


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
    # Check if not already a command
    if factname in src.commandhandler.commandList:
        return await ctx.reply("Cannot register fact: already an existing command!")
    # Check if fact doesn't already exist
    if factname in fact_index:
        return await ctx.reply("That fact already exists!")
    add_query = (f"INSERT INTO facts (FactName, FactText, FactAuthor) "
                 f"VALUES (%s, %s, %s);")
    add_data = (str(factname), str(facttext), str(ctx.sender))
    try:
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

async def remove_fact(ctx, factname: str):
    # Check if fact exists
    if factname not in fact_index:
        return await ctx.reply("That fact doesn't exist!")
    remove_query = (f"DELETE FROM facts "
                    f"WHERE factName = %s;")
    remove_data = (str(factname),)
    try:
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


async def get_facts():
    # check for connection
    if cnx is None:
        global facts
        with open('src/facts/backup_facts.json') as json_file:
            facts = json.load(json_file)
            return await update_fact_index()
    get_query = (f"SELECT factName, factText "
                 f"FROM facts")
    try:
        cursor.execute(get_query)
    except mysql.connector.Error as er:
        logging.error(f"ERROR in getting facts from DB: {er}")
    for (factName, factText) in cursor:
        facts[str(factName)] = factText
    await update_fact_index()


async def create_delayed_case(casestat, message: str, author: str):
    in_args = [int(casestat), str(message), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spCreateDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    return out_args


async def reopen_delayed_case(cID, casestat, author):
    in_args = [int(cID), int(casestat), author, 0, 0, 0]
    out_args = []
    cursor.callproc('spReopenDelayedCase', in_args)
    for result in cursor.stored_results():
        out_args.append(result.fetchall())
    out_args = list(out_args[0][0])
    return out_args
