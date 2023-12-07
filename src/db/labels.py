"""
Contains methods and classes for interacting with the 'labels' table.
"""

import sqlite3

from .. import db
from ... import config
from typing import List, Tuple, NamedTuple


class Label(NamedTuple):
    """
    Represents a single instance of a map label as stored in the
    ticker's database, including named attributes for legibility.
    """
    map_name: str
    war_number: int
    label: str
    x: float
    y:float


class NoLabelsForMapInCurrentWarException(Exception):
    """
    Represents an instance in which a query has been made to select labels
    for a specific map in a specific war, but no labels exist for it.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

def insert_label(
        map_name: str, 
        war_number: int,
        label: str, 
        x: float,
        y: float,
        conn: sqlite3.Connection
    ):
    """
    Inserts a row into the 'labels' table, uniquely identifying a specific
    labeled map location by its hex, position, and specific war.

    Args:
        map_name (str):  The systematic name of
        the map on which the label exists
        war_number (int):  The number of
        the war in which this label exists
        label (str):  The map label's text
        (i.e. the location name)
        x (float): The relative [0.0, 1.0] X position of the label
        y (float): The relative [0.0, 1.0] Y position of the label
        conn (sqlite3.Connection): A live DB connection to which to write
    """
    # Define the query, cursor, and parameters
    sql = "INSERT INTO labels VALUES (?, ?, ?, ?, ?)"
    params = (map_name, war_number, label, x, y)

    cursor = conn.cursor()

    # Execute the query on the specified database
    cursor.execute(sql, params)


def select_latest_labels_for_map(
        map_name: str, 
        conn: sqlite3.Connection
    ) -> List[Label]:
    """
    Returns a list of labels for a specified map tile in the latest war.

    Args:
        map_name (str): The systematic name of the map for which to search
        conn (sqlite3.Connection): A live database connection object to query

    Raises:
        NoLabelsForMapInCurrentWarException: Raised if there exist
        no rows in 'labels' corresponding to the highest value of
        'war_number' in the 'wars' table.

    Returns:
        Label: a list of named tuples of (map_name, war_number, label, x, y)
    """    
    # Get the number of the latest war in the DB
    latest_war, latest_pulled_on = db.wars.select_latest_war(conn)

    # Define query, cursor, and parameters
    sql = """
        SELECT
            map_name,
            war_number,
            label,
            x,
            y
        FROM labels
        WHERE 
            map_name = ?
            AND war_number = ?
    """
    params = (map_name, latest_war)
    cursor = conn.cursor()

    # Execute the query and get the list of row tuple results
    results = cursor.execute(sql, params).fetchall()

    # Check whether we got any results
    if len(results) == 0:
        # If not, raise an exception
        message = \
            f"No labels found for map {map_name} in latest war (#{latest_war})." \
            "Did PFL-TK initialize correctly?"
        raise NoLabelsForMapInCurrentWarException(message)
    else:
        # Otherwise, return the rows as named tuples
        return [Label(*row) for row in results]