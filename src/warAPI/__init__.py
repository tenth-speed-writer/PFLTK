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
    # Assemble the URL for the /maps endpoint
    root = config.war_api_roots.selected
    suffix = config.war_api_endpoints.maps
    url = root + suffix

    # Make request to the /maps endpoint
    response = requests.get(url)

    # Deserialize and return the content
    return response.json()
