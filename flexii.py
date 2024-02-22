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


bot = ezcord.bot(
    intents=intents,
    debug_guilds=[1202245624553279578],
)







if __name__ == "__main__":
    bot.load_cogs("./cogs/admin")
    bot.load_cogs("./cogs/commands")
    bot.load_cogs("./cogs/bot")
    bot.load_cogs("./cogs/events")
    bot.load_cogs("./cogs/giveway")
    bot.load_cogs("./cogs/language")


    load_dotenv()
    
    bot.run()

