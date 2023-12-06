"""
Contains methods and classes for automated testing of the behavior
of the pfltk.db package--that is, the package responsible for exposing
database interaction to the rest of the application.
"""
import pytest
import datetime
import sqlite3
from typing import List, Tuple
from ..src import db as data

from ..src.db.wars import \
    insert_war, select_latest_war, \
    UniqueRowNotFoundException, \
    UniqueRowAlreadyExistsException, \
    MultipleUniqueRowsException, \
    NoDataReturnedException

from ..src.db.maps import \
    insert_map, \
    select_latest_maps, \
    NoMapsForCurrentWarException
    
from datetime import datetime as dt

# Default DB test environment is a an in-memory DB spun up before each test,
# but this can be replaced with another environment in the future if needed.
TEST_DB_CONN_STRING = "test_storage.db"

# Our valid hypothetical war is #10 and started yesterday
VALID_WAR = (10, datetime.datetime.now() - datetime.timedelta(days=1))

# A pretend list of maps to use in fixtures for other classes' tests
VALID_MAPS: List[Tuple[str, int]] = [
    ("FoobarHex", VALID_WAR[0]),
    ("BarbazHex", VALID_WAR[0]),
    ("BazbotHex", VALID_WAR[0])
]

# Quick test to see if a given map exists
def _does_map_exist(
        map_name: str,
        war_num: int,
        conn: sqlite3.Connection
) -> bool:
    """
    Quick test of if a map exists in a given DB's 'maps' table.
    Exists as a test module function because there isn't an
    in-module method which does the same thing.

    Args:
        map_name (str): The systematic name of the map
        war_num (int): The corresponding war number of the map
        conn (sqlite3.Connection): An active SQLite3 connection

    Returns:
        bool: Whether or not a row exists for the given map and war
    """        
    sql = """
        SELECT * 
        FROM maps 
        WHERE 
            map_name = ?
            AND war_number = ?
    """
    params = (map_name, war_num)
    cursor = conn.cursor()
    results = cursor.execute(sql, params).fetchall()
    return len(results) > 0

# Setup behavior for each test is to open a new connection to an in-memory DB.
# The proper pattern for pytest fixtures is that setup logic should happen
# before a yield command, after which teardown logic is executed.
@pytest.fixture(
    scope="function" # DB teardown should happen after the end of each test
    )
def db_fixture() -> data.DB:
    """
    Fixture which prepares a configured instance of the DB class, to be
    used in the preparation of later-stage fixtures in this module.
    """
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
    
    DELETE 
    FROM sqlite_master 
    WHERE type IN (
        'table',
        'index',
        'trigger'
    );

    PRAGMA writable_schema = 0;
    
    VACUUM;
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.executescript(drop_it_all_sql)

    # Our demonstrative valid war is #10 which always started yesterday.
    # This is used in the fixtures built to prep for the tests of
    # other DB modules assessed in this test package
    valid_war: Tuple[int, datetime.datetime] = (
        10,
        datetime.datetime.now() - datetime.timedelta(days=1)
    )

@pytest.fixture(
    scope="function"
)
def valid_war_fixture(db_fixture: db_fixture):
    """
    Creates a predictable fake datum in the freshly prepared DB fixture.

    Args:
        db_fixture (db_fixture): An active instance of the fixture
        which prepares and tears down the database file and its schema.
    """
    conn = db_fixture.get_connection()
    war_num, pulled_on = VALID_WAR
    data.wars.insert_war(
        war_number=war_num,
        last_fetched_on=pulled_on,
        conn=conn
    )

    conn.commit()
    conn.close()

    yield db_fixture

@pytest.fixture(
    scope="function"
)
def valid_maps_fixture(valid_war_fixture: valid_war_fixture) -> data.DB:
    """
    Applies a known list of valid map rows to the 'maps' table, presuming
    the valid_war data used in the TestWars was already applied to the DB.
    Args:
        valid_war_fixture (TestWars.valid_war_fixture): A chained instance
        of the DB class to which a known valid war has been inserted.

    Yields:
        data.DB: The configured DB object passed to this fixture
    """
    # Get a connection to the specified test DB
    conn: sqlite3.Connection = valid_war_fixture.get_connection()

    # Insert each of this class's known test maps
    for hex_name, war_num in VALID_MAPS:
        data.maps.insert_map(hex_name, war_num, conn)

    # Commit the result
    conn.commit()

    # Yield the active DB instance we were first given
    yield valid_war_fixture


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
                conn.commit()

            insert_war(good_war_num, dt.now(), conn)
            conn.commit()

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
            conn.commit()

            with pytest.raises(Exception) as e:
                insert_war(bad_war_num, dt.now(), conn)
                conn.commit()

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


class TestMaps:
    """Contains tests for methods pertaining to the 'maps' table of the DB."""
    

    class TestInsertMap:
        """Contains tests for the maps.insert_map() function"""
        def test_inserts_new_map_in_fresh_table(
                self,
                valid_war_fixture: valid_war_fixture):
            """
            Creates a map row with valid data when no others
            exist, then makes sure that it exists.
            """
            conn = valid_war_fixture.get_connection()
            map_name = VALID_MAPS[0][0]
            war_number = VALID_MAPS[0][1]
            data.maps.insert_map(map_name, war_number, conn)

            assert _does_map_exist(map_name, war_number, conn) == True

        def test_inserts_new_map_in_non_fresh_table(
                self, 
                valid_maps_fixture: valid_maps_fixture):
            """
            Creates a map row in a table already filled with some
            amount of valid data, then makes sure all of the rows
            plus the new one are returned correctly.
            """
            conn = valid_maps_fixture.get_connection()
            map_name = "NewMapHex"
            war_number = VALID_MAPS[0][1]
            data.maps.insert_map(map_name, war_number, conn)
            maps_in_db = data.maps.select_latest_maps(conn)
            assert (map_name, war_number) in maps_in_db
    
    class TestSelectLatestMaps:
        """Contains tests for the maps.select_latest_maps() function"""
        def tests_raises_when_table_empty(self, valid_war_fixture):
            """Correctly raises an exception when the table is empty"""
            conn = valid_war_fixture.get_connection()
            with pytest.raises(NoMapsForCurrentWarException):
                result = data.maps.select_latest_maps(conn)

        def tests_returns_all_maps_when_only_one_war(self, valid_maps_fixture):
            """
            Correctly returns one result per valid map when there
            exists only one war and war's worth of maps in the DB.
            """
            conn = valid_maps_fixture.get_connection()
            assert len(data.maps.select_latest_maps(conn)) == len(VALID_MAPS)

        def tests_returns_only_latest_maps_when_multiple_wars(self, valid_maps_fixture):
            """Correctly selects only the latest war's maps."""
            # Add some newer maps
            new_maps = [
                (map_name, war_num + 1)
                for map_name, war_num
                in VALID_MAPS
            ]

            # Create a connection and add them to the DB
            conn = valid_maps_fixture.get_connection()
            for map_name, war_num in new_maps:
                insert_map(map_name, war_num, conn)

            # Get the latest war list and assert equal to the new_maps list
            results = data.maps.select_latest_maps(conn)

            assert len(results) == len(new_maps)
            assert results[0] in new_maps
            assert results[1] in new_maps
            assert results[2] in new_maps


class TestLabels:
    class TestInsertLabel:
        def test_inserts_valid_label(self):
            pass

        def test_raises_exception_for_repeat_row(self):
            pass

        def test_raises_exception_when_war_does_not_exist(self):
            pass


    class TestGetLabelsForMap:
        def test_gets_labels_when_only_one_maps_icons_exist(self):
            pass

        def test_gets_labels_when_other_maps_exist(self):
            pass

        def test_gets_labels_when_map_exists_in_past_war(self):
            pass

        def test_raises_exception_when_maps_table_empty(self):
            pass


class TestIcons:
    class TestInsertIcon:
        def test_inserts_valid_icon(self):
            pass

        def test_raises_exception_for_repeat_row(self):
            pass

        def test_raises_exception_when_war_does_not_exist(self):
            pass

        def test_raises_exception_when_map_does_not_exist(self):
            pass


    class TestGetIconsForMap:
        def test_gets_icons_when_only_one_maps_icons_exist(self):
            pass

        def test_gets_icons_when_other_maps_exist(self):
            pass

        def test_gets_icons_when_map_exists_in_past_war(self):
            pass

        def test_raises_exception_when_maps_table_empty(self):
            pass
