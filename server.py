"""Responsible for launching the client and connecting
various features to their respective endpoints."""

import discord

# Configure an Intents instance for the message_content intent
intents = discord.Intents.default()
intents.message_content = True

# Initialie the client using the specified intents
client = discord.Client(intents=intents)


