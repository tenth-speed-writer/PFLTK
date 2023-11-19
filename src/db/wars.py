import sqlite3
import datetime
import db as data

from typing import Tuple
from exceptions import \
    UniqueRowNotFoundException, \
    MultipleUniqueRowsException, \
    UniqueRowAlreadyExistsException, \
    NoDataReturnedException

from config import db_connection_string

# Spin up the database class based on the connection string in the config file
# db = data.DB(db_connection_string)

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
    def war_already_exists() -> bool:
        """
        Local function to test whether a war already exists in the database.
        """
        does_it_exist_sql = """
            SELECT * FROM wars
            WHERE war_number = ?
        """
        cursor = conn.cursor()
        cursor.execute(does_it_exist_sql)
        results = cursor.fetchall()
        if len(results) > 1:
            raise MultipleUniqueRowsException(f"Multiple rows exist for unique war number {war_number}")
        else:
            return len(results) == 1
        
    def submit_new_war(war_number, last_fetched_on) -> None:
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
            __sql=sql,
            __parameters=(war_number, fetched_on_str,))
        
        conn.commit()
    
    if war_already_exists(war_number):
        message = f"A row already exists for war number {war_number}"
        raise UniqueRowAlreadyExistsException(message)
    else:
        submit_new_war(war_number, last_fetched_on)
    

def select_latest_war(conn: sqlite3.Connection) -> Tuple[int, datetime.datetime]:
    """
    Selects the number of the latest war, as well as when that data was pulled.

    Returns:
        Tuple[int, datetime.datetime]: 
        A tuple of (war number, date pulled) corresponding to the highest
        war number recorded in the 'wars' table and when it was added.
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

    # If it returned none or more than one, throw an exception
    if len(results) == 0:
        message = \
            "No data found for latest war. " \
            "Did 'wars' populate correctly on launch?"
        raise NoDataReturnedException(message)
    elif len(results) > 1:
        # Otherwise, return the sole result
        message = "Multiple results found for latest war; error likely"
        raise MultipleUniqueRowsException(message)
    else:
        return results[0]["war_number"]
    
