"""
Fill in your bot credentials and copy this file to "config.py"
"""
from types import SimpleNamespace

# Discord bot account
discord_app_token = ""
discord_bot_account_name = ""

# SQLite3 connection string for data storage
db_connection_string = "pfltk.db" # A local SQLite3 file by default

# # # Server-specific API addresses roots
war_api_roots = SimpleNamespace()

# Able URL
war_api_roots.live_1 = 'https://war-service-live.foxholeservices.com/api/worldconquest/'

# Bravo URL
war_api_roots.live_2 = 'https://war-service-live-2.foxholeservices.com/api/worldconquest/'

# Charlie URL
war_api_roots.live_3 = 'https://war-service-live-3.foxholeservices.com/api/worldconquest/'

# Dev server URL
war_api_roots.dev = 'https://war-service-dev.foxholeservices.com/api/worldconquest/'

# Which of these links the app should use
war_api_roots.selected = war_api_roots.live_1

# # # API Endpoint Suffixes
war_api_endpoints = SimpleNamespace()

war_api_endpoints.war = "war/"
war_api_endpoints.maps = "maps/"

# Static and Dynamic data endpoints should have their map name formatted in
war_api_endpoints.static_map_data = 'maps/{map_name}/static/'
war_api_endpoints.dynamic_map_data = 'maps/{map_name}/dynamic/public'