"""
notify.py - Amazon Web Services Simple Notification Service interface

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

import re as REEE  # 🤫
from loguru import logger
from typing import List
from boto3.exceptions import Boto3Error
from halpybot import config


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


async def list_topics() -> List[str]:
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
        response = config.notify.sns.list_topics()
    except Boto3Error as boto_exception:
        raise SNSError(boto_exception) from boto_exception
    topics = response["Topics"]
    topic_list = []
    for topic, topic_type in enumerate(topics):
        topic_list.append(topic_type["TopicArn"].split(":")[5])
    return topic_list


async def subscribe(topic: str, endpoint: str):
    """Subscribe

    Adds a given email or phone number to the notification pool.

    Args:
        topic (str): The group the message is being sent to.
        endpoint (str): The Phone Number or Email for the group.

    Raises:
        ValueError: Value is neither a phone number nor email adress
        SubscriptionError: Parameters are valid but subscription could not be registered

    """

    mail = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
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
        config.notify.sns.subscribe(
            TopicArn=topic, Protocol=protocol, Endpoint=endpoint
        )
    except Boto3Error as boto_exception:
        logger.info(
            "NOTIFY: Invalid Email or Phone provided: {endpoint}. Aborting.",
            endpoint=endpoint,
        )
        raise SubscriptionError(boto_exception) from boto_exception


async def list_sub_by_topic(topic_arn: str) -> List[str]:
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
        response = config.notify.sns.list_subscriptions_by_topic(TopicArn=topic_arn)
    except Boto3Error as boto_exception:
        raise SNSError(boto_exception) from boto_exception
    subscriptions = response["Subscriptions"]
    sublist = []
    for sub, subtype in enumerate(subscriptions):
        sublist.append(subtype["Endpoint"])
    return sublist


async def send_notification(topic: str, message: str, subject: str):
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
        config.notify.sns.publish(TopicArn=topic, Message=message, Subject=subject)
    except Boto3Error as boto_exception:
        raise NotificationFailure(boto_exception) from boto_exception
