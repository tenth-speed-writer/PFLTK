"""
Manually kick starts the cold boot process and initializes the app.
Useful for testing purposes and when there's issues with Discord.
"""

from src import initialization
from config import db_connection_string

if __name__ == "__main__":
    initialization.execute_cold_start(db_connection_string)