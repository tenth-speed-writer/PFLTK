import pytest
import sqlite3

from ... import db as data
from .test_data import \
    TEST_DB_CONN_STRING, \
    VALID_WAR, \
    VALID_MAPS, \
    VALID_ICONS, \
    VALID_LABELS

@pytest.fixture(
    scope="function",
    name="foo"
)
def foo():
    yield "bar"

# Setup behavior for each test is to open a new connection to an in-memory DB.
# The proper pattern for pytest fixtures is that setup logic should happen
# before a yield command, after which teardown logic is executed.
@pytest.fixture(
    scope="function", # DB teardown should happen after the end of each test
    name="database_fixture"
)
def database_fixture():
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
    scope="function",
    name="valid_war_fixture"
)
def valid_war_fixture(database_fixture):
    """
    Creates a predictable fake datum in the freshly prepared DB fixture.

    Args:
        db_fixture (db_fixture): An active instance of the fixture
        which prepares and tears down the database file and its schema.
    """
    conn = database_fixture.get_connection()
    # war_num, pulled_on = VALID_WAR
    # data.wars.insert_war(
    #     war_number=war_num,
    #     last_fetched_on=pulled_on,
    #     conn=conn
    # )
    data.wars.insert_war(*VALID_WAR, conn)

    conn.commit()

    yield database_fixture

@pytest.fixture(
    scope="function",
    name="valid_maps_fixture"
)
def valid_maps_fixture(valid_war_fixture) -> data.DB:
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
    scope="function",
    name="valid_icons_fixture"
)
def valid_icons_fixture(valid_maps_fixture):
    # Get a connection to the specified test DB
    conn = valid_maps_fixture.get_connection()

    # Insert each of the test icons
    for icon in VALID_ICONS:
        data.icons.insert_icon(*icon, conn)
        conn.commit()

    # Yield the original fixture
    yield valid_maps_fixture

@pytest.fixture(
    scope="function",
    name="valid_labels_fixture"
)
def valid_labels_fixture(valid_maps_fixture):
    # Get a connection to the specified DB from the parent fixture
    conn = valid_maps_fixture.get_connection()

    # Insert each of the valid test labels
    for label in VALID_LABELS:
        data.labels.insert_label(*label, conn)
        conn.commit()

    # Yield the original fixture
    yield valid_maps_fixture