"""
HalpyBOT v1.4

notify.py - Amazon Web Services Simple Notification Service interface

Copyright (c) 2021 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import re as REEE  # 🤫
import logging
import boto3
import boto3.exceptions

from ..configmanager import config

class SNSError(Exception):
    """
    Base class for Halpy-SNS exceptions
    """

class NotificationFailure(SNSError):
    """
    Raised when unable to send notification
    """

class SubscriptionError(SNSError):
    """
    Could not add user to notification group
    """


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
         (str or None): Protocol if successful

     Raises:
         ValueError: Value is neither a phone number or email adress
         SubscriptionError: Parameters are valid but subscription could not be registered

     """

    mail = r'^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,24}$'
    sms = r'^\+?[1-9]\d{1,14}$'
    protocol = None

    if REEE.search(mail, endpoint):
        # Create email subscription
        protocol = 'email'

    elif REEE.search(sms, endpoint):
        # Create sms subscription
        protocol = 'sms'

    if protocol is None:
        raise ValueError

    try:
        sns.subscribe(TopicArn=topic, Protocol=protocol, Endpoint=endpoint)
    except boto3.exceptions.Boto3Error as ex:
        logging.info(f"NOTIFY: Invalid Email or Phone provided: {endpoint}. Aborting.")
        raise SubscriptionError(ex)


async def listSubByTopic(topic_arn):
    """List Subscribers

     List subscriptions by topic.

     Args:
         topic_arn (str): The group the message is being sent to.

     Returns:
         (list): All numbers, emails, etc subscribed to the topic.

     Raises:
         SNSError: Raised when query to AWS was unsuccessful

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
    return reply

async def sendNotification(topic, message, subject):
    """Send notification to a group

     Send Notifications to the specified group. Abuse this and I hunt you.

     Args:
         topic (str): The group the message is being sent to.
         message (str): The entire text of the message being sent.
         subject (str): The subject of the message, if the endpoint is an email.

     Raises:
         NotificationFailure: Raised when notification could not be sent

     """
    try:
        sns.publish(TopicArn=topic,
                    Message=message,
                    Subject=subject)
    except boto3.exceptions.Boto3Error as ex:
        raise NotificationFailure(ex)
