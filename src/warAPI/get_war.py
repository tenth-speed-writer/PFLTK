from ... import config


import requests


import datetime
from typing import Tuple


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