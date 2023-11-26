"""
Contains classes and functions for interacting with FoxHole's War API
map service. These tools are used to populate the ticker's knowledge
of the game map at the start of each war--as well as to check whether
a new war has begun.
"""
import datetime
import requests
import json
from typing import Tuple, List

from ... import config

def get_war() -> Tuple[int, datetime.datetime]:
    """
    Fetches the latest war on the server specified in the configs.
    Returns:
        Tuple[int, datetime.datetime]: A tuple of (war number, date fetched)
    """
    # Piece together the URL for the /war endpoint
    root = config.war_api_roots.selected
    suffix = config.war_api_endpoints.war
    url = root + suffix

    # Make the GET request and fetch the result
    response = requests.get(url)
    
    # Make a note of the time the request was completed
    pulled_on = datetime.datetime.now()

    # Deserialize the content, which should have a 'warNumber' attribute
    res_body = response.json()
    war_num = res_body["warNumber"]

    # Return the war number and the time of the request
    return war_num, pulled_on

def get_maps() -> List[str]:
    """
    Makes a GET request to the /maps endpoint of the War API, returning
    a list of the unique names of hexes present in this war's map.

    Returns:
        List[str]: A list of unique hex map names in the current war
    """
    # Assemble the URL for the /maps endpoint
    root = config.war_api_roots.selected
    suffix = config.war_api_endpoints.maps
    url = root + suffix

    # Make request to the /maps endpoint
    response = requests.get(url)

    # Deserialize and return the content
    return response.json()

def get_labels(
        map_name: str,
        label_type="Major") -> List[Tuple[str, int, int, str]]:
    """
    Makes a GET request to the /maps/:mapName/static endpoint, returning the
    major and minor text labels which identify the geography of that map as
    well as the hex-relative X and Y positions and "Major" or "Minor" type
    values for each of those labels.
    Args:
        map_name (str): The hex for which to pull major and minor labels.
        label_type (str, optional): "Major", "Minor", or "Both". Defaults to "Both".

    Returns:
        List[Tuple[str, int, int, str]]: A tuple containing
        (label text, x, y, and label type)
    """
    # Assemble URL, including map name parameter
    root = config.war_api_roots.selected
    suffix = config.war_api_endpoints.static_map_data.format(map_name=map_name)
    url = root + suffix

    # Make the request and parse the results to JSON.
    # Result format is: [("text", "x", "y", "mapMarkerType"), ...]
    results = requests.get(url).json()

    # Filter--if desired--by label type and return the list of tuples
    if label_type.lower() == "major":
        return [
            (item["text"], item["x"], item["y"], item["mapMarkerType"])
            for item in results["mapTextItems"]
            if item["mapMarkerType"] == "Major"
        ]
    elif label_type.lower() == "minor":
        return [
            (item["text"], item["x"], item["y"], item["mapMarkerType"])
            for item in results["mapTextItems"]
            if item["mapMarkerType"] == "Minor"
        ]
    elif label_type.lower() == "both":
        return [
            (item["text"], item["x"], item["y"], item["mapMarkerType"])
            for item in results["mapTextItems"]
        ]
    else:
        raise ValueError("label_type must be one of \"Major\", \"Minor\", or \"Both\". Got {val}".format(val=label_type))
    
def get_icons(map_name: str) -> List[Tuple[float, float, int, int]]:
    """
    Fetches a list of map icons in terms of their x & y position,
    their icon type, and their associated flags integer (a bit mask).

    Returns these as [(x, y, type, flags), ...].

    Args:
        map_name (str): The systematic name of a specific
        hex on the world map (e.g. 'TheFingersHex')

    Returns:
        List[Tuple[float, float, int, int]]: 
        A list of tuples of (x, y, icon type, icon flags)
    """
    # Assemble URL
    root = config.war_api_roots.selected
    suffix = config.war_api_endpoints.dynamic_map_data.format(map_name=map_name)
    url = root + suffix

    # Make request and get .mapItems from the result body
    results = requests.get(url).json()
    map_items = results["mapItems"]

    return [
        (item["x"], item["y"], item["iconType"], item["flags"])
        for item in map_items
    ]