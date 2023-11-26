from ... import config


import requests


from typing import List, Tuple


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