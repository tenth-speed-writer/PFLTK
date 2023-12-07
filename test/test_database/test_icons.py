import datetime
import pytest

from ...src import db as data
from ...src.db import \
    War, \
    Map, \
    Icon
from .fixtures import \
    database_fixture, \
    valid_war_fixture, \
    valid_maps_fixture, \
    valid_icons_fixture
from .test_data import \
    VALID_ICONS, \
    VALID_MAPS, \
    VALID_WAR

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
        
    
