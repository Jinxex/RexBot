import discord
import os
from dotenv import load_dotenv

import asyncio
import re
import colorama
from discord.ext import commands
from colorama import Fore
import littxlecord
from discord import Color
import random

intents = discord.Intents.all()


bot = littxlecord.Bot(
    intents=intents,
    debug_guilds=[1190258614640836659],
)





@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.streaming,
            name="cloud bot",
            url="https://twitch.tv/littxle_"
        ),
        status=discord.Status.idle,
    )




bot.add_help_command()


if __name__ == "__main__":
    bot.load_cogs("./cogs/admin", subdirectories=True, custom_log_level="admin")
    bot.load_cogs("./cogs/commmads", subdirectories=True, custom_log_level="commmads")
    bot.load_cogs("./cogs/user", subdirectories=True, custom_log_level="user")
    bot.load_cogs("./cogs/events", subdirectories=True, custom_log_level="events")
                
    load_dotenv()
    bot.run()
