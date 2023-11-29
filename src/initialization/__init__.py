"""
Contains methods and classes used when setting up the
service both for the first time and for a new war. 
"""

from .. import db
from .. import warAPI as api
from ... import config
from typing import Tuple, List
from datetime import datetime

def sync_war() -> None:
    """
    Updates the current war as it's registered in the database, including
    pulling fresh data for icons, labels, and map hex names. Will not make
    any changes if the war returned by the API isn't newer than the latest
    war on record, and will rollback if any issues are encountered in
    populating the database for the new war.
    """
    # Fetch latest war data from the API
    current_war, fetched_on: Tuple(str, datetime) = api.get_war()

    # Spin up a database connection object
    data = db.DB(config.db_connection_string)
    conn = data.get_connection()

    # Check the latest war in the database
    latest_war_on_record, latest_fetched_on: Tuple(str, datetime) \
        = db.wars.select_latest_war()

    # If the war we pulled isn't newer, break here
    if not (latest_war_on_record > current_war):
        conn.close()
        return
    
    # If this -is- a newer war, we'll start making changes to the
    # database here and commit them only if all of them succeed.

    # Create a new row in the 'wars' table for the current war
    db.wars.insert_war(
        war_number=current_war,
        last_fetched_on=fetched_on
    )

    # Get the list of map hex names for the current war
    hex_names: List[str] = api.get_maps()

    for hex_name in hex_names:
        # Add this hex to the 'maps' table

        # Get the list of major & minor map labels for this hex map.
        # These are in the format (label, x, y, label type)
        labels: List[Tuple[str, int, int, str]] = api.get_labels(
            map_name=hex_name,
            label_type="Both"
        )

        # Get the list of icons for this hex map. These are in the 
        # form of tuples of (x, y, icon type, icon flags bitmask).
        icons: List[Tuple[float, float, int, int]] = api.get_icons(
            map_name=hex_name
        )