import discord
from discord.ext import commands # ?
from discord import app_commands # ?

import configparser

import requests # API

from bs4 import BeautifulSoup # To remove the <html-tags>

# Load the bot token from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
league_api_key = config['DEFAULT']['league_api_key']






# -------------------------------------------------------------------------------------------------------------------
# Lookup Class

class Lookup(commands.Cog):

    def __init__(self, bot: commands.Bot): # Not sure what this means
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self) -> None:
        
        # Sync all commands to all servers
        await sync(self)

        print("Lookup cog is loaded & ready (1)")
        return


    



    # Lookup command
    @app_commands.command(name="lookup", description="Lookup some information about a champion")
    @app_commands.describe(champion="Name of the champion")
    @app_commands.describe(lookup_type="What to look up")
    @app_commands.choices(lookup_type=[discord.app_commands.Choice(name="Passive", value="Passive"),
                                         discord.app_commands.Choice(name="Lore", value="Lore"),
                                         discord.app_commands.Choice(name="Q", value="Q"),
                                         discord.app_commands.Choice(name="W", value="W"),
                                         discord.app_commands.Choice(name="E", value="E"),
                                         discord.app_commands.Choice(name="R", value="R")])
    async def lookup(self, interaction: discord.Interaction, champion: str, lookup_type: discord.app_commands.Choice[str]):

        # Debug Message
        # await say(interaction, f"Champ: \"{champion}\", with option: \"{lookup_option.name}\"")

        # Check if the champion name is a valid champion name
        champ_names = get_champ_names_list()
        champion = champion.capitalize()

        if not champion in champ_names: # Not Valid Champion
            await say(interaction, f"\"{champion}\" is not a valid Champion")
        else: # Valid Champion

            champion_url = f"http://ddragon.leagueoflegends.com/cdn/13.4.1/data/en_US/champion/{champion}.json?api_key={league_api_key}&champData=all&dataById=false"
            response = requests.get(champion_url)
            response.raise_for_status()  # Raises an exception for non-200 status codes

            if response.status_code == 200:
                champion_data = response.json()
                if lookup_type.name == "Lore":
                    await say_champ_lore(interaction, champion, champion_data)
                if lookup_type.name == "Q":
                    await say_champ_ability(interaction, champion, champion_data, "Q", 0)
                if lookup_type.name == "W":
                    await say_champ_ability(interaction, champion, champion_data, "W", 1)
                if lookup_type.name == "E":
                    await say_champ_ability(interaction, champion, champion_data, "E", 2)
                if lookup_type.name == "R":
                    await say_champ_ability(interaction, champion, champion_data, "R", 3)
                if lookup_type.name == "Passive":
                    await say_champ_passive(interaction, champion, champion_data)
                else:
                    await say(interaction, "Should not be able to get here i think")
            else:
                print(f"Error {response.status_code}: {response.text}")

        
# -------------------------------------------------------------------------------------------------------------------










    



# -------------------------------------------------------------------------------------------------------------------
# Helper Functions

async def say(interaction, string):
    await interaction.response.send_message(string)
    print(f"Bot said: {string}")

def get_most_recent_version():
    version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(version_url)
    version = response.json()[0]
    return version

def get_champ_names_list():

    version = get_most_recent_version()
    language = "en_US"

    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{language}/champion.json"

    response = requests.get(url)
    data = response.json()

    champion_names = [champion["name"] for champion in data["data"].values()]

    return champion_names

# A command to sync all "slash commands information"
async def sync(self):

    # Remove all previous information from all guilds?
    guilds = self.bot.guilds
    for guild in guilds:
        self.bot.tree.clear_commands(guild=guild)
    
    # Sync all commands?
    fmt = await self.bot.tree.sync()
    print(f"Synced {len(fmt)} commands to the all servers this bot is in")


# -------------------------------------------------------------------------------------------------------------------






















# -------------------------------------------------------------------------------------------------------------------
# Say Champion Information

async def say_champ_lore(interaction, champion, champion_data):

    lore = champion_data['data'][champion]['lore']

    lore = BeautifulSoup(lore, 'html.parser').get_text()

    embed = discord.Embed(
        title=f"{champion} Lore",
        description=lore,
        colour = discord.Colour.green()
    )
    await interaction.response.send_message(embed=embed)


async def say_champ_ability(interaction, champion, champion_data, ability_str, ability_value):
    ability_data = champion_data['data'][champion]['spells'][ability_value]

    desc = ""
    desc += f"Name: {ability_data['name']}\n"
    desc += f"Description: {ability_data['description']}\n"
    desc += f"Cooldown: {ability_data['cooldown']}\n"
    desc += f"Range: {ability_data['range']}"

    desc = BeautifulSoup(desc, 'html.parser').get_text()

    embed = discord.Embed(
        title=f"{champion} {ability_str}",
        description=desc,
        colour = discord.Colour.green()
    )
    await interaction.response.send_message(embed=embed)


async def say_champ_passive(interaction, champion, champion_data):

    data = champion_data['data'][champion]['passive']

    desc = BeautifulSoup(data['description'], 'html.parser').get_text()

    embed = discord.Embed(
        title=f"{champion} Passive\n{data['name']}",
        description=desc,
        colour = discord.Colour.green()
    )
    await interaction.response.send_message(embed=embed)

# -------------------------------------------------------------------------------------------------------------------







async def setup(bot):
    await bot.add_cog(Lookup(bot))
    print("Lookup cog is loaded & ready (2)")





# - Does not work to use the "say" command twice from one function?
# - Sometimes the sync command takes very long to take effect
# - All the sync command stuff is confusing, not sure if code is ideal





