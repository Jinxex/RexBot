import discord
import os
from dotenv import load_dotenv

import asyncio
import re
import colorama
from discord.commands import Option
from colorama import Fore
import nicoocord as nc
from discord import Color
import random


intents = discord.Intents.all()


bot = nc.Bot(
    intents=intents,
    debug_guilds=[1202245624553279578],
)



@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    try:
        with open('avatar.gif', 'rb') as avatar:
            await bot.user.edit(avatar=avatar.read())
        print('Animated avatar uploaded successfully!')
    except Exception as e:
        print('Failed to upload animated avatar:', e)

        

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







if __name__ == "__main__":
    bot.load_cogs("./cogs/admin")
    bot.load_cogs("./cogs/commands")
    bot.load_cogs("./cogs/bot")
    bot.load_cogs("./cogs/events")
    bot.load_cogs("./cogs/giveway")
    bot.load_cogs("./cogs/language")


    load_dotenv()
    
    bot.run()

