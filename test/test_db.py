"""
Contains methods and classes for automated testing of the behavior
of the pfltk.db package--that is, the package responsible for exposing
database interaction to the rest of the application.
"""
import pytest
import datetime
from ..src import db as data
from ..src.db.wars import \
    insert_war, select_latest_war, \
    UniqueRowNotFoundException, \
    UniqueRowAlreadyExistsException, \
    MultipleUniqueRowsException, \
    NoDataReturnedException
    
from datetime import datetime as dt

# Default DB test environment is a an in-memory DB spun up before each test,
# but this can be replaced with another environment in the future if needed.
TEST_DB_CONN_STRING = "test_storage.db"

# Setup behavior for each test is to open a new connection to an in-memory DB.
# The proper pattern for pytest fixtures is that setup logic should happen
# before a yield command, after which teardown logic is executed.
@pytest.fixture()
def db_fixture() -> data.DB:
    # Create fresh test DB environment
    db = data.DB(TEST_DB_CONN_STRING)
    db.generate_db()

    # Yield until after test execution
    yield db

    # After the test, reset the DB state by dropping everything and
    # hoping that the .db file isn't corrupted by this silly command
    drop_it_all_sql = \
    """
    PRAGMA writable_schema = 1;
    delete from sqlite_master where type in ('table', 'index', 'trigger');
    PRAGMA writable_schema = 0;
    VACUUM;
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.executescript(drop_it_all_sql)

class TestWars:
    """
    Contains tests for methods pertaining to the 'wars' table of the DB code.
    """
    class TestSelectLatestWar:
        def test_returns_none_when_no_war_exists(self, db_fixture: data.DB):
            """Tests if it returns None when no war exists"""
            conn = db_fixture.get_connection()
            latest_war = select_latest_war(conn)
            assert latest_war == None
            
        def test_returns_war_when_one_exists(self, db_fixture: data.DB):
            """If there's a row in the wars table, it returns it."""
            conn = db_fixture.get_connection()

            # Make a test row
            war_num = 42
            pulled_on = dt.now()
            insert_war(war_num, pulled_on, conn)

            # Assert that we pull it correctly
            latest_war_num, latest_pulled_on = select_latest_war(conn)
            assert latest_war_num == war_num
            assert latest_pulled_on == pulled_on

        def test_returns_right_war_when_multiple_exist(self, db_fixture: data.DB):
            """If there's multiple rows in 'wars', it returns the latest"""
            conn = db_fixture.get_connection()

            # Insert first row
            war_num_1 = 42
            pulled_on_1 = dt.now() - datetime.timedelta(days=1)
            insert_war(war_num_1, pulled_on_1, conn)

            # Insert second row
            war_num_2 = 43
            pulled_on_2 = dt.now()
            insert_war(war_num_2, pulled_on_2, conn)

            # Attempt to get the second one
            latest_war_num, latest_pulled_on = select_latest_war(conn)
            assert latest_war_num == war_num_2
            assert latest_pulled_on == pulled_on_2

    class TestInsertWar:
        """Contains tests for the wars.insert_war() method"""
        def test_single_valid_war(self, db_fixture: data.DB):
            """Should throw no errors when inserting a single valid war."""
            war_number = 32
            pulled_on = dt.now()
            conn = db_fixture.get_connection()

            # Throws no errors
            insert_war(war_number, pulled_on, conn)

            # Gets the latest war correctly
            latest_num, latest_date = select_latest_war(conn)
            assert latest_num == war_number
            assert latest_date == pulled_on
        
        def test_multiple_valid_wars(self, db_fixture: data.DB):
            """Should throw no errors when inserting multiple valid wars."""
            conn = db_fixture.get_connection()

            war_num_1 = 44
            pulled_on_1 = dt.now()
            insert_war(war_num_1, pulled_on_1, conn)

            war_num_2 = 45
            pulled_on_2 = dt.now()
            insert_war(war_num_2, pulled_on_2, conn)


        def test_negative_war_number(self, db_fixture: data.DB):
            """Throws an exception when given a negative war number"""
            conn = db_fixture.get_connection()
            bad_war_number = -21
            with pytest.raises(Exception) as e:
                insert_war(bad_war_number, dt.now(), conn)

        def test_invalid_then_valid_war(self, db_fixture: data.DB):
            """
            Raises an exception when given a bad row, but
            then works when provided with a good row.
            """
            conn = db_fixture.get_connection()
            bad_war_num = -45
            good_war_num = 32

            with pytest.raises(Exception) as e:
                insert_war(bad_war_num, dt.now(), conn)

            insert_war(good_war_num, dt.now(), conn)

            latest_war, latest_pulled_on = select_latest_war(conn)

            assert latest_war == good_war_num
                

        def test_valid_then_invalid_war(self, db_fixture: data.DB):
            """
            Inserts a good war, then raises an exception for a bad war
            """
            conn = db_fixture.get_connection()
            bad_war_num = -45
            good_war_num = 32

            insert_war(good_war_num, dt.now(), conn)

            with pytest.raises(Exception) as e:
                insert_war(bad_war_num, dt.now(), conn)

            latest_war, latest_pulled_on = select_latest_war(conn)
            assert latest_war == good_war_num

        def test_valid_then_past_war(self, db_fixture: data.DB):
            """
            Raises an exception when a past war is inserted after a current war
            """
            conn = db_fixture.get_connection()
            current_war_num = 45
            past_war_num = 44

            insert_war(current_war_num, dt.now(), conn)

            with pytest.raises(Exception):
                insert_war(past_war_num, dt.now(), conn)

            latest_war, latest_pulled_on = select_latest_war(conn)
            assert latest_war == current_war_num
            
            
