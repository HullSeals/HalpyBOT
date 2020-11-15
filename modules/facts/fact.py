"""
HalpyBOT v1.5

fact.py - Main fact module

Copyright (c) 2020 The Hull Seals,
All rights reserved

Licensed under the GNU General Public License
See license.md
"""


from typing import List
import re
import mysql.connector
import logging
import modules.commandhandler
from main import config

dbconfig = config['Database']

facts = {}

fact_index = []
basic_facts = []


cnx = mysql.connector.connect(user=dbconfig['user'],
                              password=dbconfig['password'],
                              host=dbconfig['host'],
                              database=dbconfig['database'])
print("Database connection established")

cursor = cnx.cursor()

async def on_connect():
    await get_facts()

async def clear_facts():
    facts.clear()
    fact_index.clear()
    basic_facts.clear()

async def update_fact_index():
    global fact_index
    factnames = facts.keys()
    regexp = re.compile("-")
    for name in factnames:
        if name in fact_index:
            continue
        if "_no_args" in name:
            continue
        else:
            fact_index.append(str(name))
            if not regexp.search(name) and name not in basic_facts:
                basic_facts.append(str(name))


async def add_fact(ctx, factname: str, facttext: str, reqdm: bool):
    # Check if not already a command
    if factname in modules.commandhandler.commandList:
        return await ctx.reply("Cannot register fact: already an existing command!")
    # Check if fact doesn't already exist
    if factname in fact_index:
        return await ctx.reply("That fact already exists!")
    add_query = (f"INSERT INTO facts (FactName, FactText, FactAuthor, FactReqDM) "
                 f"VALUES (%s, %s, %s, %s);")
    add_data = (str(factname), str(facttext), str(ctx.sender), reqdm)
    try:
        cursor.execute(add_query, add_data)
        cnx.commit()
        logging.info(f"FACT ADDED {factname} by {ctx.sender}")
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
        await ctx.reply("Fact removed successfully, and will disappear at next restart")
    except mysql.connector.Error as er:
        print(f"ERROR in deleting fact {factname} by {ctx.sender}: {er}")
        return await ctx.reply("Couldn't delete fact! contact a cyber")


async def get_facts():
    get_query = (f"SELECT factName, factText, factReqDM "
                 f"FROM facts")
    try:
        cursor.execute(get_query)
    except mysql.connector.Error as er:
        print(f"ERROR in getting facts from DB: {er}")
    for (factName, factText, factReqDM) in cursor:
        facts[str(factName)] = [bool(factReqDM), factText]
    await update_fact_index()

async def recite_fact(ctx, args: List[str], fact: str):

    # Check if fact is DM only
    req_dm = False
    if facts[str(fact)][0] is True:
        req_dm = True
    elif facts[str(fact)][0] is False:
        req_dm = False
    else:
        ctx.reply("Fact not properly registered! Contact a Cyberseal")

    # Check if fact is present
    if str(fact) not in facts:
        ctx.reply("Couldn't find fact! contact a Cyberseal")

    # PM only, noargs and args
    if f"{fact}_no_args" in facts and ctx.in_channel is False and req_dm is True:
        if len(args) == 0:
            return await ctx.bot.message(ctx.sender, facts[str(f"{fact}_no_args")][1])
        else:
            return await ctx.bot.message(ctx.sender, f"{' '.join(str(seal) for seal in args)}: {facts[str(fact)][1]})")

    # PM only, 1 version
    if f"{fact}_no_args" not in facts and ctx.in_channel is False and req_dm is True:
        return await ctx.bot.message(ctx.sender, facts[str(fact)][1])

    # Public and PM, 1 version
    if f"{fact}_no_args" not in facts and req_dm is False:
        if len(args) == 0:
            return await ctx.reply(facts[str(fact)][1])
        else:
            return await ctx.reply(f"{' '.join(str(seal) for seal in args)}: {facts[str(fact)][1]})")

    # Public and PM, args and noargs
    if ctx.in_channel and req_dm is False:
        if len(args) == 0:
            await ctx.bot.message(ctx.channel, facts[f"{str(fact)}_no_args"][1])
        else:
            await ctx.bot.message(ctx.channel, f"{' '.join(str(seal) for seal in args)}: {facts[str(fact)][1]}")
    elif ctx.in_channel is False:
        if len(args) == 0:
            await ctx.bot.message(ctx.sender, facts[f"{str(fact)}_no_args"][1])
        else:
            await ctx.bot.message(ctx.sender, f"{' '.join(str(seal) for seal in args)}: {facts[str(fact)][1]}")
    else:
        return
