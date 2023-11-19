"""
Contains methods and classes for automated testing of the behavior
of the pfltk.db package--that is, the package responsible for exposing
database interaction to the rest of the application.
"""
import pytest
from src import db as data

# Default DB test environment is a local DB file spun up before each test,
# but this can be replaced with a live environment in the future if needed.
TEST_DB_CONN_STRING = "pfltk_test.db"

# Setup behavior for each test is to open a new connection to an in-memory DB.
# The proper pattern for pytest fixtures is that setup logic should happen
# before a yield command, after which teardown logic is executed.
@pytest.fixture
def setup_and_teardown():
    # Create fresh test DB environment
    db = data.DB(TEST_DB_CONN_STRING)
    db.generate_db()

    # Yield until after test execution
    yield

    # Drop all tables to reset the test DB
    conn = db.get_connection()
    cursor = conn.cursor()

    # Drop-it-all command based on code from
    # https://stackoverflow.com/questions/525512/drop-all-tables-command
    drop_all_sql = """
        PRAGMA writable_schema = 1;
        DELETE FROM sqlite_master WHERE type IN (
            'table',
            'index',
            'trigger'
        );
        PRAGMA writable_schema = 0;
    """

    # Clear out the DB for the next test
    cursor.execute(drop_all_sql)

class TestWars:
    """
    Contains tests for methods pertaining to the 'wars' table of the DB code.
    """
    