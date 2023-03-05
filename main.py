
import discord
import asyncio

from discord.ext import commands
from discord import app_commands
import configparser

import os


# Get the discord token
config = configparser.ConfigParser()
config.read('config.ini')
discord_token = config['DEFAULT']['discord_token']

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=".", intents=intents) # Initialize the bot with the prefix

@bot.event
async def on_ready():
    print("Vigilant Wardstone is Online")

async def load():
    await bot.load_extension("file_1")

async def main():
    # Load the cogs
    await load()
    await bot.start(discord_token)
    bot.remove_command("help")

asyncio.run(main())



