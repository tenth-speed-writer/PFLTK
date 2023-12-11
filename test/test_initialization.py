import pytest
import sqlite3

from ..src import initialization
from ..src import db as data

from .test_database.fixtures import TEST_DB_CONN_STRING, drop_it_all_sql

@pytest.fixture
def test_db_teardown():
    """
    A fixture to tear down the test database which must necessarily
    be created in order to test the cold start functionality.
    """
    # No set up; yield immediately to the test
    yield

    # Spin up a connection and execute the drop_it_all
    # script from the test_database package on the
    # designated test database file.
    conn = sqlite3.connect(TEST_DB_CONN_STRING)
    cursor = conn.cursor()
    cursor.executescript(drop_it_all_sql)
    conn.commit()
    conn.close()


class TestInitialization:
    def test_cold_start(self, test_db_teardown):
        # Run the cold start script
        initialization.execute_cold_start(TEST_DB_CONN_STRING)
        
        # Get a connection to the provided test DB
        conn = sqlite3.connect(TEST_DB_CONN_STRING)

        # Assure each of the tables exists and is non-empty
        assert data.wars.select_latest_war(conn) is not None

        assert len(data.maps.select_latest_maps(conn)) > 0
        maps: initialization.Map = data.maps.select_latest_maps(conn)[0]

        assert len(data.labels.select_latest_labels_for_map(maps[0], conn)) > 0
        assert len(data.icons.get_latest_icons_for_map(maps[0], conn)) > 0
    
