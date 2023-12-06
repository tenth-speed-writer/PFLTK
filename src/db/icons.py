"""
Contains methods and classes for interacting with the 'icons' table.
"""
import sqlite3

from .. import db
from ... import config
from typing import List, Tuple

def insert_icon(
        map_name: str,
        war_number: int,
        x: float,
        y: float,
        icon_type: int,
        flags: int,
        conn: sqlite3.Connection
    ) -> None:
    """
    Inserts a new row into the 'icons' table, representing a single map
    location as depicted in a specific hex of a specific war, and identified
    uniquely by its relative x and y position within its hex.

    Args:
        map_name (str): The systematic name of the hex in question.
        war_number (int): The number of the war corresponding to the unique map.
        x (float): The relative (0.0-1.0) X position of the icon on its map.
        y (float): The relative (0.0-1.0) Y position of the icon on its map.
        icon_type (int): An integer specifying what
        type of site is represented by this icon.
        flags (int): An integer encoding a 6-bit flag mask for this location
        conn (sqlite3.Connection): A live database connection upon which to
        perform this insert query.
    """    
    # Define query
    query = """
        INSERT INTO icons
        VALUES (?, ?, ?, ?, ?, ?)
    """
    
    # Get cursor and define parameter tuple
    cursor = conn.cursor()
    params = (map_name, war_number, x, y, icon_type, flags)

    # Execute query
    cursor.execute(query, params)

def get_latest_icons_for_map(
        map_name: str,
        conn: sqlite3.Connection
) -> List[Tuple[str, int, float, float, int, int]]:
    """
    Selects a list of icons for a specific map hex in a specific war.
    Returns them in the format:
    
    (map name, war number, x, y, icon type, flags bitmask)

    Args:
        map_name (str): The systematic name of the hex for which to pull icons
        war_number (int): The unique number of the war associated with that map
        conn (sqlite3.Connection): A live connection object on which to query
 
    Returns:
        List[Tuple[str, int, float, float, int, int]]: A list of tuples
        in the format (map name, war number, x, y, icon type, flags bitmask)
    """
    # Get number of latest active war
    latest_war, latest_war_fetched_on = \
        db.wars.select_latest_war(conn)

    # Define query
    query = """
        SELECT *
        FROM icons
        WHERE map_name = ?
        AND war_number = ?
    """

    # Generate cursor and build params tuple
    cursor = conn.cursor()
    params = (map_name, latest_war)

    # Execute query and return results list
    result = cursor.execute(query, params)

    return result.fetchall()
