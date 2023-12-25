"""
Contains classes and methods for interacting with the
'commands' table of the database, which is responsible
for tracking all incoming command-type messages.
"""
import datetime
import sqlite3
from typing import NamedTuple
from exceptions import UniqueRowNotFoundException

class CommandData(NamedTuple):
    """
    Represents the relevant information in a single message sent
    to the bot, as it is stored in the application's database.

    Useful for inserting/selecting rows from the commands table and
    exchanging this data outside of the message or command objects.
    """
    id: int
    command: str
    user: int
    guild: str
    channel: str
    created_at: datetime.datetime
    content: str

def insert_command(data: CommandData, conn: sqlite3.connection) -> None:
    """
    Inserts a new row into the commands table representing the data shared
    by all incoming commands (such as origin and message content).

    Command data which is stored in its own table may reference
    this table's message_id field as a unique foreign key in order
    to preserve normalization.

    Args:
        data (CommandData): A CommandData object containing the information 
        for an incoming command message.
        conn (sqlite3.connection): An active SQLite3 connection object to
        the application's active database instance.
    """    
    # Define query
    query = 'INSERT INTO commands VALUES (?, ?, ?, ?, ?, ?, ?)'

    # Get cursor and execute parameterized query
    cursor = conn.cursor()
    cursor.execute(query, data)

def select_command(id: int, conn: sqlite3.Connection) -> CommandData:
    """
    Returns a CommandData object for a single command on record in the DB,
    provided with its unique message_id and a valid connection to that DB.

    Args:
        id (int): The unique message ID to search for
        conn (sqlite3.Connection): A connection to a DB on which to search

    Raises:
        UniqueRowNotFoundException: Represents a situation in which no row
        was found in the 'commands' table for the specified message_id.

    Returns:
        CommandData: The data of the matching row in the 'commands' table.
    """    
    # Define query and sole parameter
    query = """
        SELECT 
            message_id,
            command,
            user,
            guild,
            created_at,
            content
        FROM commands
        WHERE message_id = ?
    """
    params = (id,)

    # Get cursor, execute query, and fetch results list
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()

    # Raise a specific exception if no result was returned
    if len(results) == 0:
        message = f"No command found in DB with message_id = {str(id)}"
        raise UniqueRowNotFoundException(message)
    
    # Otherwise, return the sole result
    else:
        return CommandData(*results[0])
