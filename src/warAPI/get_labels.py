from ... import config


import requests


from typing import List, Tuple


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
        (label text, x, y, label type)
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