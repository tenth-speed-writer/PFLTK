import config
import requests
from typing import List


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
    response = requests.get(url, timeout=30)

    # Deserialize and return the content
    return response.json()