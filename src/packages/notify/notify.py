"""
HalpyBOT v1.4

notify.py - Amazon Web Services Simple Notification Service interface

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import re
import logging
import boto3

from ..configmanager import config

if config['Notify']['secret'] and config['Notify']['access']:
    sns = boto3.client("sns",
                       region_name=config['Notify']['region'],  # AWS Region.
                       aws_access_key_id=config['Notify']['access'],  # AWS IAM Access Key
                       aws_secret_access_key=config['Notify']['secret'])  # AWS IAM Secret
else:
    sns = None

async def listTopics():
    """Subscribe

     List all SNS topics on the given account.

     Args:
         None.

     Returns:
         (str): A list of all topics configured in common-name format.

     """
    # List all SNS Topics on the Acct
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
    reply = f"I can notify these groups: {reply}"  # We cut the full ARNs down to just the "common names" at the end.
    return reply


async def subscribe(topic, endpoint):
    """Subscribe

     Adds a given email or phone number to the notification pool.

     Args:
         topic (str): The group the message is being sent to.
         endpoint (str): The Phone Number or Email for the group.

     Returns:
         (str): Confirmation of subscription or an error.

     """
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,24}$'
    regex2 = '^\+?[1-9]\d{1,14}$'
    if re.search(regex, endpoint):
        # Create email subscription
        sns.subscribe(TopicArn=topic, Protocol='email', Endpoint=endpoint)
        shorttopic = topic.split(":")
        reply = f"Subscription of {endpoint} to topic {shorttopic[5]} over Email pending confirmation."
    elif re.search(regex2, endpoint):
        # Create sms subscription
        sns.subscribe(TopicArn=topic, Protocol='sms', Endpoint=endpoint)
        shorttopic = topic.split(":")
        reply = f"Successfully subscribed {endpoint} to topic {shorttopic[5]} over SMS."
    else:
        logging.debug("Invalid Email or Phone provided: '%s'! Aborting.", endpoint)
        reply = "Invalid Email or Phone. No subscription generated."
    return reply


async def listSubByTopic(topic_arn, short_topic):
    """List Subscribers

     List subscriptions by topic.

     Args:
         topic_arn (str): The group the message is being sent to.
         short_topic (str): The friendly name of the group.

     Returns:
         (str): All numbers, emails, etc subscribed to the topic.

     """
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
            reply = str(reply) + ", " + str(member)
        i += 1
    reply = f"The following endpoints are subscribed to the {short_topic} group: {reply}"
    return reply


async def sendNotification(topic, message, subject):
    """Send Notifications

     Send Notifications to the specified group. Abuse this and I hunt you.

     Args:
         topic (str): The group the message is being sent to.
         message (str): The entire text of the message being sent.
         subject (str): The subject of the message, if the endpoint is an email.

     Returns:
         (str): Either the error code of a failed sending attempt or a confirmation that the message was sent.

     """
    try:
        sns.publish(TopicArn=topic,
                    Message=message,
                    Subject=subject)
        shorttopic = topic.split(":")
        status = f"Message Sent to group {shorttopic[5]}. Please only send one message per issue!"
    except sns.exceptions as e:
        status = f"ERROR!: {str(e)}"
    return status
