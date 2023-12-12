"""
Contains methods and classes for interacting
with the 'tickets' table of the database.
"""
import sqlite3
from datetime import datetime
from collections import NamedTuple
from exceptions import \
    UniqueRowNotFoundException, \
    MultipleUniqueRowsException

class Ticket(NamedTuple):
    """Represents a single Ticket as it exists in memory or in the database."""
    # Associated war
    war_number: int

    # A destination label & description is required
    destination_map_name: str
    destination_x: float
    destination_y: float
    destination_description: str

    # An origin label & description are optional
    origin_map_name: str | None
    origin_x: float | None
    origin_y: float | None
    origin_description: str | None

    # A text description of the ticket and when it was submitted
    objective_description: str
    created_on: datetime

def insert_ticket(
    ticket: Ticket, 
    conn: sqlite3.Connection
) -> None:
    """
    Inserts a new ticket into the database.

    Args:
        ticket (Ticket): A Ticket object to be inserted
        conn (sqlite3.Connection): A connection to a database hosting
        this application into which this ticket will be inserted.
    """
    # Determine whether we have all the data to submit the origin
    has_valid_origin = \
        ticket.origin_map_name is not None \
        and ticket.origin_x is not None \
        and ticket.origin_y is not None \
        and ticket.origin_description is not None
    
    if has_valid_origin:
        # If given a valid origin, use the full query
        query = """
            INSERT INTO tickets
            VALUES ?,?,?,?,?,?,?,?,?,?,?
        """
        params = ticket
    else:
        # If not given a full valid origin, just submit the rest
        query = """
            INSERT INTO tickets (
                war_number,
                destination_map_name,
                destination_x,
                destination_y,
                objective_description,
                created_on
            ) VALUES ?,?,?,?,?,?
        """
        params = (
            ticket.war_number,
            ticket.destination_map_name,
            ticket.destination_x,
            ticket.destination_y,
            ticket.objective_description,
            ticket.created_on
        )
        
    
    # In either case: create a cursor and execute the query
    cursor = conn.cursor()

    cursor.execute(query, params)
    conn.commit()

def select_ticket(
    ticket_number: int,
    conn: sqlite3.Connection
) -> Ticket:
    """
    Selects a specific ticket provided with its ticket number and a
    live connection to the database which supports the application.

    Args:
        ticket_number (int): The ID of the ticket to select
        conn (sqlite3.Connection): A live SQLite3 connection

    Returns:
        Ticket: A Ticket NamedTuple containing the specified row
    """
    # Define query and (single-element) parameters tuple
    query = "SELECT * FROM tickets WHERE ticket_number = ?"
    params = (ticket_number,)

    # Get cursor and execute query
    cursor = conn.cursor()
    results = cursor.execute(query, params).fetchall()

    # Throw an exception if zero or more than one result were returned
    if len(results) == 0:
        message = f"No ticket found with ID {ticket_number}"
        raise UniqueRowNotFoundException(message)
    elif len(results) > 1:
        message = f"Duplicate rows found for unique ticket ID {ticket_number}"
        raise MultipleUniqueRowsException(message)
    
    # Otherwise, return the result as a named tuple
    return Ticket(*results[0])
