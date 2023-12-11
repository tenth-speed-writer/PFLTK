"""
Contains methods and classes used when setting up the
service both for the first time and for a new war. 
"""
import sqlite3
import config
from .. import db
from ..db import War, Map, Label, Icon
from .. import warAPI as api
from typing import Tuple, List
from datetime import datetime

def execute_cold_start(connection_string: str = config.db_connection_string):
    """
    Initializes database, loads static resources to it, and runs sync_war().

    Args:
        connection_string (str, optional): DB connection string. 
        Defaults to config.db_connection_string.
    """    
    # Create database connection
    data = db.DB(connection_string)
    conn = data.get_connection()

    # Implement database schema
    data.generate_db()

    # Synchronize with the current war
    sync_war(conn)

    # If no issues at all occurred, commit the changes
    conn.commit()
    conn.close()

def sync_war(conn: sqlite3.Connection) -> None:
    """
    Updates the current war as it's registered in the database, including
    pulling fresh data for icons, labels, and map hex names. Will not make
    any changes if the war returned by the API isn't newer than the latest
    war on record, and will rollback if any issues are encountered in
    populating the database for the new war.

    Args:
        connection_string (str, optional): Conn string for the
        database in which the application should be initialized.
        Defaults to config.db_connection_string, but can be set
        to an alternative value for testing purposes.
    """
    # Fetch latest war data from the API
    current_war = War(*api.get_war())

    # Check the latest war in the database
    latest_war_in_db = db.wars.select_latest_war(conn)

    # If the war we pulled isn't newer, break here--ignoring the
    # check if there is no previous war and the call returned None
    if latest_war_in_db is None:
        pass
    elif not (current_war.war_number > latest_war_in_db.war_number):
        return
    
    # If this -is- a newer war, we'll start making changes to the
    # database here and commit them only if all of them succeed.

    # Create a new row in the 'wars' table for the current war
    db.wars.insert_war(*current_war, conn)

    # Get the list of map hex names for the current war
    hex_names: List[str] = api.get_maps()
    maps: List[Map] = [Map(hex, current_war.war_number) for hex in hex_names]

    # Add each map's labels and icons to the database
    for map_ in maps:
        # Add this hex to the 'maps' table
        db.maps.insert_map(*map_, conn)
        conn.commit()

        # Get the list of major & minor map labels for this hex map.
        # These are in the format (map name, war number, label, x, y)
        labels: List[Label] = [
            Label(map_.map_name, map_.war_number, *label_tuple[:3])
            for label_tuple in api.get_labels(
                map_name=map_.map_name,
                label_type="Both"
            )
        ]

        # Insert the labels
        for label in labels:
            db.labels.insert_label(*label, conn)
        conn.commit()

        # Get the list of icons for this hex map. These are in the 
        # form of tuples of (x, y, icon type, icon flags bitmask).
        icons: List[Icon] = [
            Icon(map_.map_name, map_.war_number, *icon_tuple)
            for icon_tuple in api.get_icons(
                map_name=map_.map_name
            )
        ]

        # Insert the icons
        for icon in icons:
            db.icons.insert_icon(*icon, conn)
        
    

__all__ = [
    "sync_war",
    "execute_cold_start"
]