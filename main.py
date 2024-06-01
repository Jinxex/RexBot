import discord
import os
from dotenv import load_dotenv
from ezcord import i18n
import asyncio
import re
import colorama
from discord.commands import Option
from colorama import Fore
import ezcord
import yaml
from discord import Color
import random

intents = discord.Intents.all()

bot = ezcord.Bot(
    intents=intents,
    error_handler=(os.getenv("ERROR_WEBHOOK_URL")),
)



with open("en.yaml", encoding="utf-8") as file:
    en = yaml.safe_load(file)

with open("de.yaml", encoding="utf-8") as file:
    de = yaml.safe_load(file)

string_locals = {"en": en, "de": de}
ezcord.i18n.I18N(string_locals)








if __name__ == "__main__":
    bot.load_cogs()


    bot.run()