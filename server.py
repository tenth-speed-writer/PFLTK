"""Responsible for launching the client and connecting
various features to their respective endpoints."""

import discord
import config

# Get the bot's token from the config file
token = config.discord_app_token

# Configure an Intents instance for the message_content intent
intents = discord.Intents.default()
intents.message_content = True

# Initialize the client using the specified intents
client = discord.Client(intents=intents)

# Set an event to announce in log when ready
@client.event
async def on_ready():
    print(f'PFL-TK logged in as {client.user}')

# Set an event to handle incoming messages
@client.event
async def on_message(message: discord.Message):
    response = \
        f'Greetings {message.author}. Your message reads: {message.content}'
    
    await message.channel.send(response)

if __name__ == "__main__":
    client.run(token=token)