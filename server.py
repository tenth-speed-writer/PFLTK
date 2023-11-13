"""
Responsible for launching the client and connecting
various features to their respective endpoints.

Can be called as a script to host PFL-TK with configs
provided by the file 'configs.py'. If you pulled this project
from GitHub, make a copy of 'config_template.py' populated
with your own bot account token and so on.
"""

import discord
import config
from logging import Logger

# Set up logging
log = Logger("PFL-TK Log")

# Get the bot's token and name from the config file
token = config.discord_app_token
own_name = config.discord_bot_account_name

# Configure an Intents instance for the message_content intent
intents = discord.Intents.default()
intents.message_content = True

# Initialize the client using the specified intents
client = discord.Client(intents=intents)

# Set an event to announce in log when ready
@client.event
async def on_ready():
    log.info(f'PFL-TK logged in as {client.user}')

# Set an event to handle incoming messages
@client.event
async def on_message(message: discord.Message):
    if message.author != own_name:
        response = \
            f'Greetings {message.author}. Your message reads: {message.content}'
        await message.channel.send(response)

# If this file was called directly as a script, host the bot.
if __name__ == "__main__":
    client.run(token=token)
