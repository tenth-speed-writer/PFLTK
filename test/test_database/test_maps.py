import sqlite3
import pytest
import datetime

from fixtures import *
from test_data import \
    VALID_MAPS, \
    VALID_WAR
from src import db as data
from src.db import \
    NoDataReturnedException, \
    War

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
                data.maps.insert_map(map_name, war_num, conn)

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