import discord
import os
import ezcord
import rexapi

intents = discord.Intents.all()

bot = ezcord.Bot(
    intents=intents,
    error_handler=(os.getenv("ERROR_WEBHOOK_URL")),
)



if __name__ == "__main__":
    bot.load_cogs()


    bot.run()