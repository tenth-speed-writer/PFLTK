"""
Contains methods and classes for interacting with the 'labels' table.
"""

from .. import db
from ... import config
from typing import List, Tuple

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
        y: float
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
    """
    
    # Generate a connection object
    data = db.DB(config.db_connection_string)
    conn = data.get_connection()

    # Define the query, cursor, and parameters
    sql = "INSERT INTO labels VALUES (?, ?, ?, ?, ?)"
    params = (map_name, war_number, label, x, y)
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(sql, params)

    # Commit changes and close connection
    conn.commit()
    conn.close()

def select_latest_labels_for_map(map_name: str) \
    -> List[Tuple[str, int, str, float, float]]:
    """
    Returns a list of labels for a specified map tile in the latest war.

    Raises:
        NoLabelsForMapInCurrentWarException: Raised if there exist
        no rows in 'labels' corresponding to the highest value of
        'war_number' in the 'wars' table.

    Returns:
        List[Tuple[str, int, str, float, float ]]: A list of row tuples
        of (map name, war number, label, x position, y position)
    """    
    # Create a DB connection object
    data = db.DB(config.db_connection_string)
    conn = data.get_connection()

    # Get the number of the latest war in the DB
    latest_war = db.wars.select_latest_war()

    # Define query, cursor, and parameters
    sql = """
        SELECT (
            map_name,
            war_number,
            label,
            x,
            y
        )
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
        conn.close()
        message = \
            f"No labels found for map {map_name} in latest war (#{latest_war})." \
            "Did PFL-TK initialize correctly?"
        raise NoLabelsForMapInCurrentWarException(message)
    else:
        # Otherwise, return them
        return results