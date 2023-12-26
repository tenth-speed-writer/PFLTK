"""
Contains methods for interacting with the database instance which powers
this application. By default this is a local SQLite file in its host
filesystem, but this could hypothetically be replaced with a remote
connection string in the config.py file.
"""

from .db import DB
from .exceptions import \
    MultipleUniqueRowsException, \
    UniqueRowNotFoundException, \
    NoDataReturnedException, \
    UniqueRowAlreadyExistsException, \
    MapDoesNotExistInCurrentWarException

from . import wars
from .wars import \
    War, \
    NewerWarAlreadyExistsException

from . import maps
from .maps import \
    Map, \
    NoMapsForCurrentWarException

from . import labels
from .labels import \
    Label, \
    NoLabelsForMapInCurrentWarException

from . import icons
from .icons import \
    Icon

from . import tickets
from .tickets import \
    Ticket, \
    CannotCreateTicketForWarException

from . import commands
from .commands import \
    CommandData

from . import users
from users import \
    User

__all__ = [
    # Core module and shared exceptions
    "db",
    "MultipleUniqueRowsException",
    "UniqueRowNotFoundException",
    "NoDataReturnedException",
    "UniqueRowAlreadyExistsException",
    "MapDoesNotExistInCurrentWarException",

    # Wars module
    "wars",
    "War",
    "NewerWarAlreadyExistsException",

    # Maps module
    "maps",
    "Map",
    "NoMapsForCurrentWarException",

    # Labels module
    "labels",
    "Label",
    "NoLabelsForMapInCurrentWarException",

    # Icons module
    "Icon",
    "icons",

    # Tickets module
    "Ticket",
    "tickets",
    "CannotCreateTicketForWarException"

    # Commands module
    "CommandData",
    "commands"

    # Users module
    "User",
    "users"
]