import discord
from discord.commands import slash_command, Option
import littxlecord
from discord.ext import commands
from littxlecord import View

class Report(littxlecord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = 817435791079768105






    @slash_command(
        description="Send a DM owner report about the bot!"
    )
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def report(self, ctx, reason: Option(str, description="Describe your problem in more detail and where the error lies")):
        owner_user = await self.bot.fetch_user(self.owner_id)

        embed = discord.Embed(
            title=f"Report from {ctx.author.display_name}",
            description=reason,
            color=discord.Color.red()
        )

        dm_channel = await owner_user.create_dm()
        await dm_channel.send(embed=embed)

        await ctx.respond("Your report has been sent. Thank you", ephemeral=True)

def setup(bot):
    bot.add_cog(Report(bot))