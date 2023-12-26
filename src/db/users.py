"""Contains methods and data objects for interacting with the 'users' table."""
import sqlite3
from enum import Enum
from typing import NamedTuple
from exceptions import UniqueRowNotFoundException

class Role(Enum):
    """
    The valid roles which can be assigned to a user on a server.
    """
    # Teamsters may take and fulfill tickets on this server.
    TEAMSTER="teamster"

    # Submitters may also create new tickets on this server.
    SUBMITTER="submitter"

    # Supervisors may create tickets and may assign or unassign
    # the roles of teamster and submitter on this server.
    SUPERVISOR="supervisor"

    # Admins may assign or unassign supervisor roles on this server.
    # This role might also be used when determining whether a user
    # is allowed to change a server-wide setting or similar.
    ADMIN="admin"


class User(NamedTuple):
    """
    Represents the data corresponding to a single known user on a
    single discord server, as well as the role assigned to them,
    as represented in the application database.
    """
    user_id: int
    guild: str
    role: Role

def insert_or_update_user(user: User, conn: sqlite3.connection) -> None:
    """
    Inserts a new row into the 'users' table, provided with the user's
    discord ID, the role to give them, and the server on which to give it.

    Args:
        user (User): A NamedTuple of user_id, server, and role to assign
        conn (sqlite3.connection): An active SQLite3 connection to the
        application database, onto which to insert this row.
    """
    # Generate query and assign parameters, making sure to get
    # the value of the enumerated argument instead of its name
    query = "INSERT INTO users VALUES (?, ?, ?)"
    params = (*user[0:2], user[2].name)

    # Create a cursor and execute the query
    cursor = conn.cursor()
    cursor.execute(query, params)

def select_user_role(user_id: int, guild: str, conn: sqlite3.Connection) -> Role:
    """
    Selects the role of a given user on a given server by their user ID
    and the name of the server in question. Throws a specific exception
    if the row doesn't exist.

    Args:
        user_id (int): The discord user ID to search for
        guild (str): The discord server on which to search
        conn (sqlite3.Connection): An active SQLite3 connection to
        the live application database

    Raises:
        UniqueRowNotFoundException: Raised if there exists no
        role for the specified user ID on the specified server

    Returns:
        Role: An enumerative value corresponding to the user's role
    """    
    # Define query and parameters
    query = """
        SELECT
            role
        FROM users
        WHERE 
            user_id = ?
            AND guild = ?
    """
    params = (user_id, guild)

    # Get cursor, execute query, and fetch results
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()

    # Raise an exception if no results were returned
    if len(results) == 0:
        message = f"No user role found for user {user_id} on server {guild}."
        raise UniqueRowNotFoundException(message)
    
    # Otherwise return the sole result as an enum value
    else:
        return Role[results[0]]
