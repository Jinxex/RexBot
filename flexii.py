import discord
import os
from dotenv import load_dotenv

import asyncio
import re
import colorama
from discord.commands import Option
from colorama import Fore
import ezcord
from discord import Color
import random

intents = discord.Intents.all()


bot = ezcord.Bot(
    intents=intents,
    debug_guilds=[1202245624553279578],
    error_webhook_url=(os.getenv("ERROR_WEBHOOK_URL"))
)


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.streaming,
            name="Flexii",
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
    bot.load_cogs("./cogs/tempvoice", subdirectories=True, custom_log_level="tempvoice")
    bot.load_cogs("./cogs/giveway", subdirectories=True, custom_log_level="giveway")
    bot.load_cogs("./cogs/language", subdirectories=True, custom_log_level="language")


    load_dotenv()
    
    bot.run()
