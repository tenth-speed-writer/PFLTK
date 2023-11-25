import pytest

from ..src import warAPI as api

class TestGetWar:
    def test_gets_war_number_correctly(self):
        """Assures it can correctly get the war number from the API"""
        war_num, pulled_on = api.get_war()

        assert 0 < war_num
        assert war_num < 1000

class TestGetMaps:
    def tests_gets_maps_correctly(self):
        """Assures it can correctly get the list of map names"""

        # There should be fingers in the result
        map_to_check = "TheFingersHex"
        results = api.get_maps()

        # Check for fingers~
        assert map_to_check in results