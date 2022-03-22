"""
HalpyBOT v1.6

notify.py - Amazon Web Services Simple Notification Service interface

Copyright (c) 2022 The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import re as REEE  # 🤫
from loguru import logger
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


if config["Notify"]["secret"] and config["Notify"]["access"]:
    sns = boto3.client(
        "sns",
        region_name=config["Notify"]["region"],  # AWS Region.
        aws_access_key_id=config["Notify"]["access"],  # AWS IAM Access Key
        aws_secret_access_key=config["Notify"]["secret"],
    )  # AWS IAM Secret
else:
    sns = None


async def list_topics():
    """Subscribe

    List all SNS topics on the given account.

    Args:
        None.

    Returns:
        (list): A list of all topics configured in common-name format.

    Raises:
        SNSError: Raised when topic list could not be retrieved from AWS

    """
    # List all SNS Topics on the Acct
    try:
        response = sns.list_topics()
    except boto3.exceptions.Boto3Error as boto_exception:
        raise SNSError(boto_exception) from boto_exception
    topics = response["Topics"]
    topic_list = []
    for topic in range(len(topics)):
        topic_list.append(topics[topic]["TopicArn"].split(":")[5])
    return topic_list


async def subscribe(topic, endpoint):
    """Subscribe

    Adds a given email or phone number to the notification pool.

    Args:
        topic (str): The group the message is being sent to.
        endpoint (str): The Phone Number or Email for the group.

    Returns:
        (str or None): Protocol if successful

    Raises:
        ValueError: Value is neither a phone number nor email adress
        SubscriptionError: Parameters are valid but subscription could not be registered

    """

    mail = r"^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,24}$"
    sms = r"^\+?[1-9]\d{1,14}$"
    protocol = None

    if REEE.search(mail, endpoint):
        # Create email subscription
        protocol = "email"

    elif REEE.search(sms, endpoint):
        # Create sms subscription
        protocol = "sms"

    if protocol is None:
        raise ValueError

    try:
        sns.subscribe(TopicArn=topic, Protocol=protocol, Endpoint=endpoint)
    except boto3.exceptions.Boto3Error as boto_exception:
        logger.info(
            "NOTIFY: Invalid Email or Phone provided: {endpoint}. Aborting.",
            endpoint=endpoint,
        )
        raise SubscriptionError(boto_exception) from boto_exception


async def list_sub_by_topic(topic_arn):
    """List Subscribers

    List subscriptions by topic.

    Args:
        topic_arn (str): The group the message is being sent to.

    Returns:
        (list): All numbers, emails, etc. subscribed to the topic.

    Raises:
        SNSError: Raised when query to AWS was unsuccessful

    """
    try:
        response = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
    except boto3.exceptions.Boto3Error as boto_exception:
        raise SNSError(boto_exception) from boto_exception
    subscriptions = response["Subscriptions"]
    sublist = []
    for sub in range(len(subscriptions)):
        sublist.append(subscriptions[sub]["Endpoint"])
    return sublist


async def send_notification(topic, message, subject):
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
        sns.publish(TopicArn=topic, Message=message, Subject=subject)
    except boto3.exceptions.Boto3Error as boto_exception:
        raise NotificationFailure(boto_exception) from boto_exception
