"""
Contains methods and classes for interacting with the 'wars' table.
"""

import sqlite3
import datetime
from . import db as data

from typing import Tuple
from .exceptions import \
    UniqueRowNotFoundException, \
    MultipleUniqueRowsException, \
    UniqueRowAlreadyExistsException, \
    NoDataReturnedException

from ...config import db_connection_string

# Spin up the database class based on the connection string in the config file
# db = data.DB(db_connection_string)

class NewerWarAlreadyExistsException(Exception):
    """
    Represents an instance in which a row cannot be submitted to the
    'wars' table because a row with a higher war number already exists.
    """
    def __init__(
            self,
            proposed_war_number: int, 
            latest_war_number:int
        ) -> None:
        message = \
            f"Cannot create a row for war #{proposed_war_number}; " \
            f"a newer entry already exists for war #{latest_war_number}."
        super().__init__(message)

def insert_war(
        war_number: int,
        last_fetched_on: datetime.datetime,
        conn: sqlite3.Connection):
    """
    Inserts a new row into the 'wars' table representing a new war
    on the server being monitored by this instance of the ticker.

    Args:
        war_number (int):
            The integer number of the new war
        last_fetched_on (datetime.datetime):
            When this data was pulled from the API
        conn (sqlite3.Connection):
            An open SQLite3 connection object
    """
    def _war_already_exists(war_num: int) -> bool:
        """
        Local function to test whether a war already exists in the database.
        """
        does_it_exist_sql = """
            SELECT * FROM wars
            WHERE war_number = ?
        """
        cursor = conn.cursor()
        cursor.execute(
            does_it_exist_sql, 
            (war_num,)
        )
        results = cursor.fetchall()
        if len(results) > 1:
            raise MultipleUniqueRowsException(f"Multiple rows exist for unique war number {war_number}")
        else:
            return len(results) == 1
        
    def _submit_new_war(war_number, last_fetched_on) -> None:
        """
        Local function which creates a new row in the 'wars' table.
        """
        # Define query text
        sql = """
            INSERT INTO wars
            VALUES (
                ?,
                ?
            )
        """

        # Parse fetched-on date
        fetched_on_str = data.DB.format_date_for_db(last_fetched_on)
        
        # Get cursor and execute
        cursor = conn.cursor()
        
        # Execute the command
        cursor.execute(
            sql,
            (war_number, fetched_on_str,)
        )
        
        conn.commit()
    
    # Assure the war number is valid
    if (war_number < 0):
        raise ValueError("war_number must be an integer not less than 0")
    
    # See if this war already exists
    if (_war_already_exists(war_number)):
        message = f"Entry for war number {war_number} already exists"
        raise UniqueRowAlreadyExistsException(message)
    
    # See if a more recent war already exists
    latest_war_tuple: Tuple[int, datetime.datetime] | None = \
        select_latest_war(conn)
    
    # It's fine if the given war is newer or if there's no existing wars.
    newer_war_exists = \
        not(latest_war_tuple == None) and (latest_war_tuple[0] > war_number)
    # Otherwise, raise an exception.
    if newer_war_exists:
        raise NewerWarAlreadyExistsException(
            proposed_war_number=war_number,
            latest_war_number=latest_war_tuple[0]
        )
    
    # If neither rejecting condition is true, submit the given row
    _submit_new_war(war_number, last_fetched_on)
    

def select_latest_war(conn: sqlite3.Connection) -> Tuple[int, datetime.datetime] | None:
    """
    Selects the number of the latest war, as well as when that data was pulled.

    Will return None if there are no wars in the database when called.

    Returns:
        Tuple[int, datetime.datetime] | None: 
        A tuple of (war number, date pulled) corresponding to the highest
        war number recorded in the 'wars' table and when it was added.
        None if no values were found.
    """    
    # We use this format rather than a SELECT TOP (1) query so we can
    # add verification that there's only one entry for the current war.
    latest_war_sql = """
        SELECT 
            war_number,
            last_fetched_on
        FROM wars
        WHERE war_number = (
            SELECT MAX(war_number) FROM wars
        )
    """

    # Spin up a cursor and get the results
    cursor = conn.cursor()
    results = cursor.execute(latest_war_sql).fetchall()

    # Check how many results we got, expecting zero or one.
    if len(results) > 1:
        # Throw an exception if we somehow got multiple unique rows
        message = "Multiple results found for latest war; error likely"
        raise MultipleUniqueRowsException(message)
    elif len(results) == 0:
        # Return None if there's no data
        return None
    else:
        # Otherwise, return a tuple of (war_number, date_pulled)
        war_num, pulled_on = results[0][0], data.DB.format_date_from_db(results[0][1])
        return (war_num, pulled_on)
    
