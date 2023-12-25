import pytest

#from .fixtures import *
from fixtures import \
    database_fixture, \
    valid_war_fixture, \
    valid_maps_fixture, \
    valid_labels_fixture
from src import db as data
from test_data import \
    VALID_MAPS, \
    VALID_LABELS

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

        def test_raises_exception_when_maps_table_empty(
            self,
            database_fixture
        ):
            # Get connection
            conn = database_fixture.get_connection()

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