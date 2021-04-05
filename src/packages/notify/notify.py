"""
HalpyBOT v1.4

notify.py - Amazon Web Services Simple Notification Service interface

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import boto3
import logging
import re
from ..configmanager import config


logger = logging.getLogger(__name__)

sns = boto3.client("sns",
                   region_name=config['Notify']['region'], #AWS Region
                   aws_access_key_id=config['Notify']['access'], #AWS IAM Access Key
                   aws_secret_access_key=config['Notify']['secret']) #AWS IAM Secret

async def listTopics():
    #List all SNS Topics on the Acct
    response = sns.list_topics()
    topics = response["Topics"]
    numTopics = len(topics)
    i = 0
    reply = None
    while i < numTopics:
        member = response["Topics"][i]["TopicArn"]
        parts = member.split(":")
        if reply is None:
            reply = str(parts[5])
        else:
            reply = str(reply) + ", " + str(parts[5])
        i += 1
    reply = f"I can notify these groups: {reply}"
    return reply

async def subscribe(topic, endpoint):
    #Subscribe a phone number to SMS over SNS
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,24}$'
    regex2 = '^\+?[1-9]\d{1,14}$'
    if (re.search(regex, endpoint)):
        # Create email subscription
        sns.subscribe(TopicArn=topic, Protocol='email', Endpoint=endpoint)
        shorttopic = topic.split(":")
        reply = f"Subscription of {endpoint} to topic {shorttopic[5]} over Email pending confirmation."
    elif (re.search(regex2, endpoint)):
        # Create sms subscription
        sns.subscribe(TopicArn=topic, Protocol='sms', Endpoint=endpoint)
        shorttopic = topic.split(":")
        reply = f"Successfully subscribed {endpoint} to topic {shorttopic[5]} over SMS."
    else:
        logger.exception("Invalid Email or Phone provided: '%s'! Aborting.", endpoint)
        reply = "Invalid Email or Phone. No subscription generated."
    return reply


async def listSubByTopic(topic_arn, shorttopic):
    # List subscriptions by topic
    response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
    subscriptions = response["Subscriptions"]
    numSubs = len(subscriptions)
    i = 0
    reply = None
    while i < numSubs:
        member = response["Subscriptions"][i]["Endpoint"]
        if reply is None:
            reply = str(member)
        else:
            reply = str(reply) + ", "+ str(member)
        i += 1
    reply = f"The following endpoints are subscribed to the {shorttopic} group: {reply}"
    return reply


async def sendNotification(topic, message, subject):
    try:
        sns.publish(TopicArn=topic,
                    Message=message,
                    Subject=subject)
        shorttopic = topic.split(":")
        status = f"Message Sent to group {shorttopic[5]}. Please only send one message per issue!"
    except Exception as e:
        status =  f"ERROR!: {str(e)}"
    return status
