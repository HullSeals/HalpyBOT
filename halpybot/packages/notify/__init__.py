"""
__init__.py - Initilization for boto3 notification module

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from .notify import (
    list_topics,
    list_sub_by_topic,
    subscribe,
    send_notification,
    SNSError,
    SubscriptionError,
    NotificationFailure,
)

__all__ = [
    "list_topics",
    "list_sub_by_topic",
    "subscribe",
    "send_notification",
    "SNSError",
    "SubscriptionError",
    "NotificationFailure",
]
