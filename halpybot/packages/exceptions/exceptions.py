"""
exceptions.py - All Custom HalpyBOT Exceptions

Copyright (c) The Hull Seals,
All rights reserved.

Licensed under the GNU General Public License
See license.md
"""


class YOURLSError(Exception):
    """
    Base class for YOURLS link errors
    """


class YOURLSNoResponse(YOURLSError):
    """
    An exception occurred while sending data to or receiving from a YOURLS API
    """


class YOURLSBadResponse(YOURLSError):
    """
    YOURLS returned an unprocessable response.
    """


class CommandException(Exception):
    """
    Base exception for all commands
    """


class CommandHandlerError(CommandException):
    """
    Base exception for command errors
    """


class CommandAlreadyExists(CommandHandlerError):
    """
    Raised when a command is registered twice
    """


class AnnouncementError(Exception):
    """
    Could not announce request
    """


class AlreadyExistsError(AnnouncementError):
    """
    Case from Announcement already exists
    """


class KFCoordsError(AnnouncementError):
    """
    Given Kingfisher Coordinates were not Floatable
    """


class FactHandlerError(Exception):
    """
    Base class for fact handler exceptions
    """


class FactUpdateError(FactHandlerError):
    """
    Unable to update a fact attribute to the database
    """


class InvalidFactException(FactHandlerError):
    """
    Raised when an invalid fact is created
    """


class DiscordWebhookError(Exception):
    """
    Base class for Discord webhook errors
    """


class WebhookSendError(DiscordWebhookError):
    """
    An exception occurred while sending a Discord Webhook
    """


class EDSMLookupError(Exception):
    """
    Base class for lookup errors
    """


class NoResultsEDSM(EDSMLookupError):
    """
    No results for the given query were found with the EDSM API
    """


class EDSMConnectionError(EDSMLookupError):
    """
    Request failed due to an exception that occurred
    while connecting to the EDSM API
    """


class NoNearbyEDSM(EDSMLookupError):
    """
    No results for the given query were found with the EDSM API within a specified distance.
    """


class EDSMReturnError(EDSMLookupError):
    """
    EDSM returned a reply, however the reply did not include key data needed to continue.
    """


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


class UserError(Exception):
    """
    Base class for User Class errors
    """


class NoUserFound(UserError):
    """
    An exception occurred while sending a Discord Webhook
    """
