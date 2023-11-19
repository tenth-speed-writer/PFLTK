import sqlite3
import datetime

from db import DB

def insert_war(
        war_number: int,
        last_fetched_on: datetime.datetime,
        conn: sqlite3.Connection):
    # Define query text
    sql = \
        """
        INSERT INTO wars
        VALUES (
            ?,
            ?
        )
        """
    
    # Parse fetched-on date
    fetched_on_str = DB.format_date_for_db(last_fetched_on)
    
    # Get cursor and execute
    cursor = conn.cursor()
    
    cursor.execute(
        __sql=sql,
        __parameters=(war_number, fetched_on_str,))

def select_latest_war():
    pass