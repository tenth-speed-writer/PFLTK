"""
Contains classes and functions for interacting with FoxHole's War API
map service. These tools are used to populate the ticker's knowledge
of the game map at the start of each war--as well as to check whether
a new war has begun.
"""
__all__ = [
    "get_war",
    "get_maps",
    "get_icons",
    "get_labels"
]

from .get_war import get_war
from .get_maps import get_maps
from .get_icons import get_icons
from .get_labels import get_labels
