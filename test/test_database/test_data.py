import datetime

from typing import List, Tuple
from src.db import War, Map, Icon, Label

# Default DB test environment is a an in-memory DB spun up before each test,
# but this can be replaced with another environment in the future if needed.
TEST_DB_CONN_STRING = "test_storage.db"

# Our valid hypothetical war is #10 and started yesterday
VALID_WAR = War(10, datetime.datetime.now() - datetime.timedelta(days=1))

# A pretend list of maps to use in fixtures for other classes' tests
VALID_MAPS: List[Tuple[str, int]] = [
    Map("FoobarHex", VALID_WAR[0]),
    Map("BarbazHex", VALID_WAR[0]),
    Map("BazbotHex", VALID_WAR[0])
]

# Map name, war number, x, y, icon type, flags
VALID_ICONS: List[Tuple[str, int, float, float, int, int]] = [
    Icon(VALID_MAPS[0][0], VALID_MAPS[0][1], 0.25, 0.3, 25, 0),
    Icon(VALID_MAPS[0][0], VALID_MAPS[0][1], 0.35, 0.02, 25, 0),
    Icon(VALID_MAPS[1][0], VALID_MAPS[1][1], 0.275, 0.9, 25, 0),
    Icon(VALID_MAPS[1][0], VALID_MAPS[1][1], 0.1283, 0.949, 25, 0),
    Icon(VALID_MAPS[2][0], VALID_MAPS[2][1], 0.0120, 0.1412, 25, 0),
    Icon(VALID_MAPS[2][0], VALID_MAPS[2][1], 0.58, 0.445, 25, 0)
]

# Map name, war number, label text, x, y
VALID_LABELS: List[Tuple[str, int, str, float, float]] = [
    Label(VALID_MAPS[0][0], VALID_MAPS[0][1], "Thing A", 0.24, 0.93),
    Label(VALID_MAPS[0][0], VALID_MAPS[0][1], "Thing B", 0.95, 0.43),
    Label(VALID_MAPS[1][0], VALID_MAPS[1][1], "Stuff A", 0.19, 0.40),
    Label(VALID_MAPS[1][0], VALID_MAPS[1][1], "Stuff B", 0.85, 0.65),
    Label(VALID_MAPS[2][0], VALID_MAPS[2][1], "Junk A", 0.24, 0.398),
    Label(VALID_MAPS[2][0], VALID_MAPS[2][1], "Junk B", 0.94, 0.211)
]