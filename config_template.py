"""
Fill in your bot credentials and copy this file to "config.py"
"""
from types import SimpleNamespace

# Discord bot account
discord_app_token = ""
discord_bot_account_name = ""

# SQLite3 connection string for data storage
db_connection_string = "pfltk.db" # A local SQLite3 file by default

# Server-specific API addresses roots
war_api_endpoints = SimpleNamespace()
war_api_endpoints.live_1 = 'https://war-service-live.foxholeservices.com/api/'
war_api_endpoints.live_2 = 'https://war-service-live-2.foxholeservices.com/api/'
war_api_endpoints.live_3 = 'https://war-service-live-3.foxholeservices.com/api/'
war_api_endpoints.dev = 'https://war-service-dev.foxholeservices.com/api/'