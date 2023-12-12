"""
Contains methods and classes for interacting
with the 'tickets' table of the database.
"""
import sqlite3
from datetime import datetime
from typing import NamedTuple
from .exceptions import \
    UniqueRowNotFoundException, \
    MultipleUniqueRowsException, \
    MapDoesNotExistException, \
    MapDoesNotExistInCurrentWarException, \
    NoDataReturnedException
from .wars import War
from .maps import Map
from .db import DB


class CannotCreateTicketForWarException(Exception):
    """
    Represents an instance where a ticket cannot be created for a specified
    war, either because that war specified is in the past or future.
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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
) -> int:
    """
    Inserts a new ticket into the database, returning its row ID.
    Will include an origin location and description if provided with
    all 4 related arguments, but ignores it if missing any of them.

    Args:
        ticket (Ticket): A Ticket object to be inserted
        conn (sqlite3.Connection): A connection to a database hosting
        this application into which this ticket will be inserted.

    Returns:
        int: The ticket ID of the newly created row
    """
    def _assert_war_is_real_and_current(
        war_number: int,
        conn: sqlite3.Connection
    ):
        """
        Throws exceptions if there are no wars, or if the specified war
        does not correspond to the active war as per the 'wars' table.
        """
        query = """SELECT * FROM wars"""
        cursor = conn.cursor()

        cursor.execute(query)
        wars = [War(*row) for row in cursor.fetchall()]

        # Check for an empty wars table
        if len(wars) == 0:
            message = \
                "No data found in table 'wars'. " \
                "Was the app initialized correctly?"
            raise NoDataReturnedException(message)
        
        # Check for a past or future war
        newest_war = max([war.war_number for war in wars])
        if war_number < newest_war:
            message = \
                f"Cannot create ticket; war #{war_number}" \
                f" is earlier than current war #{newest_war}."
            raise CannotCreateTicketForWarException(message)
        elif war_number > newest_war:
            message = \
                f"Cannot create ticket set in war #{war_number},"\
                f" as the latest war on record is #{newest_war}."
            raise CannotCreateTicketForWarException(message)

    def _assert_map_is_real_and_current(
        map_name: str,
        war_number: int,
        conn: sqlite3.Connection
    ):
        """
        Throws an exception a specified origin or destination map doesn't
        exist, either in the current war or in the database entirely.
        """
        # Define query and get cursor
        query = "SELECT map_name, war_number FROM maps"
        cursor = conn.cursor()
        cursor.execute(query)
        maps = [Map(*map_) for map_ in cursor.fetchall()]

        print(maps)

        if map_name not in set([map_.map_name for map_ in maps]):
            message = \
                f"No map by the name {map_name} exists" \
                " in the 'maps' for any war on record."
            raise MapDoesNotExistException(message)
        elif Map(map_name, war_number) not in maps:
            message = \
                f"No map found named {map_name} for current war #{war_number}."
            raise MapDoesNotExistInCurrentWarException(message)

    # Perform exception checking for everything except origin
    _assert_war_is_real_and_current(ticket.war_number, conn)
    _assert_map_is_real_and_current(
        map_name=ticket.destination_map_name,
        war_number=ticket.war_number,
        conn=conn)

    # Determine whether we have all the data to submit the origin
    has_valid_origin = \
        ticket.origin_map_name is not None \
        and ticket.origin_x is not None \
        and ticket.origin_y is not None \
        and ticket.origin_description is not None
    
    # Perform exception checking--if appropriate--for origin as well
    if has_valid_origin:
        _assert_map_is_real_and_current(
            map_name=ticket.origin_map_name,
            war_number=ticket.war_number,
            conn=conn)
    
    if has_valid_origin:
        # If given a valid origin, use the full query
        query = """
            INSERT INTO tickets (
                war_number,
                
                destination_map_name,
                destination_x,
                destination_y,
                destination_description,

                origin_map_name,
                origin_x,
                origin_y,
                origin_description,

                objective_description,
                created_on
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
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
                destination_description,

                objective_description,
                created_on
            ) VALUES (?,?,?,?,?,?,?)
        """
        params = (
            ticket.war_number,
            ticket.destination_map_name,
            ticket.destination_x,
            ticket.destination_y,
            ticket.destination_description,
            ticket.objective_description,
            ticket.created_on
        )
        
    
    # In either case: create a cursor and execute the query
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

    # Return the cursor's lastrowid to identify the new row
    return cursor.lastrowid

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
    
    # Otherwise, return the result as a named tuple (excluding the ID).
    # Be sure as well to re-format its date type.
    result = results[0]
    return Ticket(*result[1:-1], DB.format_date_from_db(result[-1]))
