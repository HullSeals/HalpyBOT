"""
__init__.py - Initilization for the Exceptions module

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""

from .exceptions import (
    YOURLSError,
    YOURLSNoResponse,
    YOURLSBadResponse,
    CommandHandlerError,
    CommandException,
    CommandAlreadyExists,
    AnnouncementError,
    AlreadyExistsError,
    KFCoordsError,
    FactUpdateError,
    FactHandlerError,
    InvalidFactException,
    DiscordWebhookError,
    WebhookSendError,
    EDSMLookupError,
    EDSMReturnError,
    EDSMConnectionError,
    NoResultsEDSM,
    NoNearbyEDSM,
    SNSError,
    SubscriptionError,
    NotificationFailure,
    UserError,
    NoUserFound,
)

__all__ = [
    "YOURLSError",
    "YOURLSNoResponse",
    "YOURLSBadResponse",
    "CommandException",
    "CommandAlreadyExists",
    "CommandHandlerError",
    "AnnouncementError",
    "AlreadyExistsError",
    "KFCoordsError",
    "FactHandlerError",
    "FactUpdateError",
    "InvalidFactException",
    "DiscordWebhookError",
    "WebhookSendError",
    "EDSMConnectionError",
    "EDSMReturnError",
    "EDSMLookupError",
    "NoNearbyEDSM",
    "NoResultsEDSM",
    "SubscriptionError",
    "SNSError",
    "NotificationFailure",
    "UserError",
    "NoUserFound",
]
