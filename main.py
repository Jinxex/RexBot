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
async def on_member_join(member):
    role_ids = [1183612004846534708, 1183612004846534709]
    for role_id in role_ids:
        role = member.guild.get_role(role_id)
        await member.add_roles(role)


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
    bot.load_cogs("cogs", subdirectories=True)
                
    load_dotenv()
    bot.run()
