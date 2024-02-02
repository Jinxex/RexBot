import discord
from discord.commands import slash_command, Option
import ezcord

class Language(ezcord.Cog):

    @slash_command()
    async def set(
        self,
        ctx,
        language: Option(str, description="Choose the language", choices=["Deutsch", "English","Russia"])
    ):
        await ctx.respond(f"You have changed the bot's language to {language}!")


def setup(bot):
    bot.add_cog(Language(bot))