"""
Contains methods and classes for interacting with the 'maps' table.
"""

import sqlite3

from typing import Tuple, List
from .. import db
from ... import config


class NoMapsForCurrentWarException(Exception):
    """
    Represents an instance in which a current war exists in the
    database, but no rows in the 'maps' table exist for it.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def insert_map(map_name: str, war_number: int) -> None:
    """
    Inserts a new row into the 'maps' table, representing a
    unique hex on the map of a uniquely identified war.
    Args:
        map_name (str): The systematic name of the
        hex in question (e.g. "TheFingersHex")
        war_number (int): The number of the war in which this map exists
    """
    # Spin up a DB connection object
    data = db.DB(config.db_connection_string)
    conn = data.get_connection()

    # Define query and create cursor
    sql = "INSERT INTO maps VALUES (?, ?)"
    cursor = conn.cursor()

    # Execute query
    params = map_name, war_number
    cursor.execute(sql, params)

def select_latest_maps() -> List[Tuple[str, int]]:
    """_summary_

    Raises:
        NoMapsForCurrentWarException: Raised when there is no map data
        available for the current war, either because it's outdated or
        because no map data has yet been inserted into the database.

    Returns:
        List[Tuple[str, int]]: 
        A list of results as [(map_name, war_number), ...]
    """     
    # Spin up a DB connection object
    data = db.DB(config.db_connection_string)
    conn = data.get_connection()

    # Identify the latest war number
    latest_war, latest_war_fetched_on = db.wars.select_latest_war()

    # Define query and create cursor
    sql = """
        SELECT
            map_name,
            war_number
        FROM maps
        WHERE 
            war_number = {}
    """
    cursor = conn.cursor()
    params = (latest_war,)

    # Execute query
    results = cursor.execute(sql, params).fetchall()

    if len(results) == 0:
        # If there were no results, raise an exception
        message = \
            f"No maps found for latest war (#{latest_war}). " \
            "Was PFL-TK initialized correctly?"
        raise NoMapsForCurrentWarException(message)
    else:
        # Otherwise, return the list of (map_name, war_num) tuples
        return results
    
