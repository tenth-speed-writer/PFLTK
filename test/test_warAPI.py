import pytest

from ..src import warAPI as api

class TestGetWar:
    """Contains methods for testing the warAPI.get_war() method"""
    def test_gets_war_number_correctly(self):
        """Assures it can correctly get the war number from the API"""
        war_num, pulled_on = api.get_war()

        assert 0 < war_num
        assert war_num < 1000

class TestGetMaps:
    """Contains methods for testing the warAPI.get_maps() method"""
    def tests_gets_maps_correctly(self):
        """Assures it can correctly get the list of map names"""

        # There should be fingers in the result
        map_to_check = "TheFingersHex"
        results = api.get_maps()

        # Check for fingers~
        assert map_to_check in results

class TestGetLabels:
    """Contains methods for testing the warAPI.get_labels() method"""
    # Constants to test with
    map_hex = "TheFingersHex"
    known_fingers_major_label = "Captain's Dread"
    known_fingers_minor_label = "Cavitatis"

    def test_gets_all_labels_correctly(self):
        """Assures it fetches lists of major labels"""
        # Get its labels
        result = api.get_labels(
            map_name=self.map_hex,
            label_type="Both"
        )

        # Assert the list of "text" attributes of the contents of
        # result["mapTextItems"] contains our desired major & minor labels
        texts = [text for text, x, y, label_type in result]

        assert self.known_fingers_major_label in texts
        assert self.known_fingers_minor_label in texts
    
    def test_gets_major_labels_correctly(self):
        """Assures it fetches a list of only major labels"""
        # Get its labels
        result = api.get_labels(
            map_name=self.map_hex,
            label_type="Major"
        )

        # Assert the list of "text" attributes of the contents of
        # result["mapTextItems" contains our desired major label
        # and NOT our known minor label.

        texts = [text for text, x, y, label_type in result]

        assert self.known_fingers_major_label in texts
        assert not (self.known_fingers_minor_label in texts)

    def test_gets_minor_labels_correctly(self):
        """Assures it fetches a list of only minor labels"""
        # Assert the list of "text" attributes of the contents of
        # result["mapTextItems"] contains our desired minor label
        # and NOT our known major label.
        result = api.get_labels(
            map_name=self.map_hex,
            label_type="Minor"
        )

        texts = [text for text, x, y, label_type in result]

        assert not (self.known_fingers_major_label in texts)
        assert self.known_fingers_minor_label in texts

    def test_raises_value_error_for_bad_label_type(self):
        """
        Assures a label_type besides 'Major', 'Minor', or 'Both'
        raises a ValueError from the function.
        """

        with pytest.raises(ValueError):
            api.get_labels(self.map_hex, "doobie")
    
    
