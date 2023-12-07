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

from ..src.db import \
    War, \
    Map, \
    Label, \
    Icon

from ..src.db.maps import \
    insert_map, \
    select_latest_maps, \
    NoMapsForCurrentWarException
    
from datetime import datetime as dt

# Default DB test environment is a an in-memory DB spun up before each test,
# but this can be replaced with another environment in the future if needed.
TEST_DB_CONN_STRING = "test_storage.db"

# Our valid hypothetical war is #10 and started yesterday
VALID_WAR = War(10, datetime.datetime.now() - datetime.timedelta(days=1))

# A pretend list of maps to use in fixtures for other classes' tests
VALID_MAPS: List[Tuple[str, int]] = [
    Map("FoobarHex", VALID_WAR[0]),
    Map("BarbazHex", VALID_WAR[0]),
    Map("BazbotHex", VALID_WAR[0])
]

# Map name, war number, x, y, icon type, flags
VALID_ICONS: List[Tuple[str, int, float, float, int, int]] = [
    Icon(VALID_MAPS[0][0], VALID_MAPS[0][1], 0.25, 0.3, 25, 0),
    Icon(VALID_MAPS[0][0], VALID_MAPS[0][1], 0.35, 0.02, 25, 0),
    Icon(VALID_MAPS[1][0], VALID_MAPS[1][1], 0.275, 0.9, 25, 0),
    Icon(VALID_MAPS[1][0], VALID_MAPS[1][1], 0.1283, 0.949, 25, 0),
    Icon(VALID_MAPS[2][0], VALID_MAPS[2][1], 0.0120, 0.1412, 25, 0),
    Icon(VALID_MAPS[2][0], VALID_MAPS[2][1], 0.58, 0.445, 25, 0)
]

# Map name, war number, label text, x, y
VALID_LABELS: List[Tuple[str, int, str, float, float]] = [
    Label(VALID_MAPS[0][0], VALID_MAPS[0][1], "Thing A", 0.24, 0.93),
    Label(VALID_MAPS[0][0], VALID_MAPS[0][1], "Thing B", 0.95, 0.43),
    Label(VALID_MAPS[1][0], VALID_MAPS[1][1], "Stuff A", 0.19, 0.40),
    Label(VALID_MAPS[1][0], VALID_MAPS[1][1], "Stuff B", 0.85, 0.65),
    Label(VALID_MAPS[2][0], VALID_MAPS[2][1], "Junk A", 0.24, 0.398),
    Label(VALID_MAPS[2][0], VALID_MAPS[2][1], "Junk B", 0.94, 0.211)
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
    # war_num, pulled_on = VALID_WAR
    # data.wars.insert_war(
    #     war_number=war_num,
    #     last_fetched_on=pulled_on,
    #     conn=conn
    # )
    data.wars.insert_war(*VALID_WAR, conn)

    conn.commit()

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

@pytest.fixture(
    scope="function"
)
def valid_icons_fixture(valid_maps_fixture: valid_maps_fixture):
    # Get a connection to the specified test DB
    conn = valid_maps_fixture.get_connection()

    # Insert each of the test icons
    for icon in VALID_ICONS:
        data.icons.insert_icon(*icon, conn)
        conn.commit()

    # Yield the original fixture
    yield valid_maps_fixture

@pytest.fixture(
    scope="function"
)
def valid_labels_fixture(valid_maps_fixture: valid_maps_fixture):
    # Get a connection to the specified DB from the parent fixture
    conn = valid_maps_fixture.get_connection()

    # Insert each of the valid test labels
    for label in VALID_LABELS:
        data.labels.insert_label(*label, conn)
        conn.commit()

    # Yield the original fixture
    yield valid_maps_fixture

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
            with pytest.raises(NoDataReturnedException):
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
        
        def tests_raises_exception_when_latest_maps_dont_match_latest_war(
            self,
            valid_maps_fixture
        ):
            # Get connection
            conn = valid_maps_fixture.get_connection()

            # Create and insert a newer war
            new_war = War(
                war_number=VALID_WAR.war_number + 1,
                pulled_on=VALID_WAR.pulled_on + datetime.timedelta(days=30)
            )


class TestLabels:
    """Contains methods for testing the db.labels module"""
    class TestInsertLabel:
        """Contains tests for the labels.insert_label() method"""
        def test_inserts_valid_label(self, valid_maps_fixture):
            # Get a connection to the test DB
            conn = valid_maps_fixture.get_connection()

            # Attempt to insert a valid row
            map_name, war_number, label, x, y = VALID_LABELS[0]
            data.labels.insert_label(
                map_name=map_name,
                war_number=war_number,
                label=label,
                x=x,
                y=y,
                conn=conn
            )

            # Commit and see if it inserted correctly
            conn.commit()
            rows = data.labels.select_latest_labels_for_map(
                map_name=map_name,
                conn=conn
            )
            
            assert VALID_LABELS[0] in rows

        def test_raises_exception_for_repeat_row(self, valid_labels_fixture):
            # Get a connection to a DB with the VALID_LABELS already in it
            conn = valid_labels_fixture.get_connection()

            # Get an example of a valid but repeated row
            map_name, war_number, label, x, y = VALID_LABELS[0]

            # Assert that inserting one again raises an exception
            with pytest.raises(Exception):
                data.labels.insert_label(
                    map_name,
                    war_number,
                    label,
                    x,
                    y,
                    conn
                )

        def test_raises_exception_when_war_does_not_exist(
                self,
                valid_labels_fixture
        ):
            # Get connection
            conn = valid_labels_fixture.get_connection()

            # Assert inserting a row for a fake war raises an exception
            map_name, real_war_number, label, x, y = VALID_LABELS[0]
            fake_war_number = 855

            with pytest.raises(Exception):
                data.labels.insert_label(map_name, fake_war_number, label, x, y)


    class TestGetLabelsForMap:
        """
        Contains tests for the select_latest_labels_for_map() method
        """
        def test_gets_labels_when_only_one_maps_labels_exist(
                self,
                valid_war_fixture
        ):
            # Get connection
            conn = valid_war_fixture.get_connection()

            # Insert a single label
            data.labels.insert_label(*VALID_LABELS[0], conn)
            conn.commit()

            # Get latest labels for the map named in the first valid label
            labels = data.labels.select_latest_labels_for_map(VALID_LABELS[0][0], conn)

            assert VALID_LABELS[0] in labels

        def test_gets_right_labels_when_other_maps_exist(
                self,
                valid_labels_fixture
        ):
            # Get connection
            conn = valid_labels_fixture.get_connection()

            # Get labels for one of the maps
            map_name = VALID_MAPS[0][0]
            labels = data.labels.select_latest_labels_for_map(map_name, conn)

            # Assure the results contain its labels
            assert VALID_LABELS[0] in labels
            assert VALID_LABELS[1] in labels

            # Assure the results DON'T contain the other labels
            assert VALID_LABELS[2] not in labels
            assert VALID_LABELS[3] not in labels
            assert VALID_LABELS[4] not in labels
            assert VALID_LABELS[5] not in labels

        def test_raises_exception_when_maps_table_empty(self, db_fixture):
            # Get connection
            conn = db_fixture.get_connection()

            # Attempt to insert a row, expecting an exception
            map_name, war_number, label, x, y = VALID_LABELS[0]
            with pytest.raises(Exception):
                data.labels.insert_label(
                    map_name,
                    war_number,
                    label,
                    x,
                    y
                )


class TestIcons:
    class TestInsertIcon:
        def test_inserts_valid_icon(self, valid_maps_fixture):
            """Tests that it inserts a valid icon in an empty table."""
            conn = valid_maps_fixture.get_connection()
            icon = VALID_ICONS[0]

            data.icons.insert_icon(*icon, conn)
            conn.commit()

            # Assert that it then fetches that row
            icons = data.icons.get_latest_icons_for_map(icon[0], conn)
            assert icon in icons

        def test_raises_exception_for_repeat_row(self, valid_maps_fixture):
            """Tests that it raises when a repeat row is inserted"""
            # Get a connection and a valid demo row
            conn = valid_maps_fixture.get_connection()
            icon = VALID_ICONS[0]

            # Insert it once
            data.icons.insert_icon(*icon, conn)
            conn.commit()

            # Try to insert it again, expecting an exception
            with pytest.raises(Exception):
                data.icons.insert_icon(*icon, conn)

        def test_raises_exception_when_war_does_not_exist(self, valid_icons_fixture):
            # Get a connection
            conn = valid_icons_fixture.get_connection()

            # Create a modified version of the first valid test icon,
            # assigning it to a future war_number not in the DB
            i = VALID_ICONS[0]
            icon = (i[0], i[1] + 1, i[2], i[3], i[4])

            with pytest.raises(Exception):
                data.icons.insert_icon(icon, conn)

        def test_raises_exception_when_map_does_not_exist(self, valid_maps_fixture):
            # Get a connection
            conn = valid_maps_fixture.get_connection()

            # Make up a map
            bad_hex_name = "TheToesHex"

            # Make a bad icon row based on it
            i = VALID_ICONS[0]
            icon = (bad_hex_name, *i[1:])

            # Try to insert it
            with pytest.raises(Exception):
                data.icons.insert_icon(icon, conn)


    class TestGetIconsForMap:
        def test_gets_icons_when_only_one_maps_icons_exist(self, valid_maps_fixture):
            # Get a connection
            conn = valid_maps_fixture.get_connection()

            # Insert two rows for the same map
            data.icons.insert_icon(*VALID_ICONS[0], conn)
            conn.commit()

            data.icons.insert_icon(*VALID_ICONS[1], conn)
            conn.commit()

            # Select them
            icons = data.icons.get_latest_icons_for_map(
                map_name=VALID_ICONS[0][0],
                conn=conn
            )

            # Assert there's nothing in it but those two rows 
            assert len(icons) == 2
            assert VALID_ICONS[0] in icons
            assert VALID_ICONS[1] in icons
        
        def test_gets_icons_when_other_maps_exist(self, valid_icons_fixture):
            # Get a connection
            conn = valid_icons_fixture.get_connection()

            # Select icons for one map
            map_name = VALID_ICONS[0][0]
            icons = data.icons.get_latest_icons_for_map(map_name, conn)

            # Assure the results don't contain other maps' hex names
            result_map_names = [i[0] for i in icons]
            assert map_name in result_map_names
            assert VALID_ICONS[2][0] not in result_map_names
            assert VALID_ICONS[4][0] not in result_map_names
        

        def test_gets_icons_when_map_exists_in_past_war(self, valid_war_fixture):
            # Get a connection
            conn = valid_war_fixture.get_connection()

            # Add a new war
            new_war = War(
                war_number=VALID_WAR.war_number + 1,
                pulled_on=VALID_WAR.pulled_on + datetime.timedelta(days=30)
            )
            data.wars.insert_war(*new_war, conn)
            conn.commit()

            # Add one of the test maps for the new war
            new_map = Map(
                VALID_MAPS[0].map_name,
                new_war.war_number
            )
            data.maps.insert_map(*new_map, conn)
            conn.commit()

            # Add an icon to that new test map
            new_icon = Icon(
                map_name=new_map.map_name,
                war_number=new_map.war_number,
                x=VALID_ICONS[0].x,
                y=VALID_ICONS[0].y,
                icon_type=VALID_ICONS[0].icon_type,
                flags=VALID_ICONS[0].flags
            )
            data.icons.insert_icon(*new_icon, conn)
            conn.commit()

            # Select the new map-war's icons
            icons = data.icons.get_latest_icons_for_map(new_map[0], conn)
            assert new_icon in icons

        def test_raises_exception_when_maps_table_empty(self, valid_war_fixture):
            # Get a connection
            conn = valid_war_fixture.get_connection()

            # Ensure trying to get icon data when the maps table
            # is empty raises a NoDataReturnedException
            with pytest.raises(data.NoDataReturnedException):
                data.icons.get_latest_icons_for_map(VALID_MAPS[0][0], conn)
        
        def tests_raises_exception_when_maps_table_incomplete(
                self,
                valid_war_fixture
        ):
            # Get a connection
            conn = valid_war_fixture.get_connection()

            # Insert a map
            data.maps.insert_map(*VALID_MAPS[0], conn)
            conn.commit()

            # Try to select an icon from a different map
            with pytest.raises(data.MapDoesNotExistInCurrentWarException):
                data.icons.get_latest_icons_for_map(VALID_MAPS[2][0], conn)

        def tests_raises_exception_when_maps_not_updated_for_war(
                self,
                valid_icons_fixture
        ):
            # Get a connection
            conn = valid_icons_fixture.get_connection()
            new_war = War(
                war_number=VALID_WAR.war_number + 1,
                pulled_on=VALID_WAR.pulled_on + datetime.timedelta(days=35)
            )
            # Insert a new war, but not its first map
            data.wars.insert_war(*new_war, conn)
            conn.commit()

            data.maps.insert_map(
                VALID_MAPS[1].map_name,
                VALID_MAPS[1].war_number + 1,
                conn)
            conn.commit()

            print(f"Latest war is {data.wars.select_latest_war(conn)}")
            print(f"Latest maps are {data.maps.select_latest_maps(conn)}")

            # Try to select icons from somewhere on the map in that war
            with pytest.raises(data.MapDoesNotExistInCurrentWarException):
                data.icons.get_latest_icons_for_map(VALID_MAPS[0].map_name, conn)
        
    
