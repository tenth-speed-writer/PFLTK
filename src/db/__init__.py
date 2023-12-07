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
    NewerWarAlreadyExistsException

from . import maps
from .maps import \
    NoMapsForCurrentWarException

from . import labels
from .labels import \
    NoLabelsForMapInCurrentWarException

from . import icons

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
    "NewerWarAlreadyExistsException",

    # Maps module
    "maps",
    "NoMapsForCurrentWarException",

    # Labels module
    "labels",
    "NoLabelsForMapInCurrentWarException"

    # Icons module
    "icons"
]