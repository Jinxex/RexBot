import discord
from discord.commands import slash_command, Option
from discord.ext import commands

class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = 817435791079768105

    @slash_command(
        description="Send a DM owner report about the bot!"
    )
    @discord.guild_only()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def bug(self, ctx, reason: str, img: Option(discord.Attachment, description="Attach an image (optional)")): # type: ignore
        owner_user = await self.bot.fetch_user(self.owner_id)

        embed = discord.Embed(
            title=f"Report from {ctx.author.display_name}",
            description=reason,
            color=discord.Color.red()
        )

        if img is not None:
            embed.set_image(url=img.url)

        dm_channel = await owner_user.create_dm()
        await dm_channel.send(embed=embed)

        await ctx.respond("Your report has been sent. Thank you", ephemeral=True)

def setup(bot):
    bot.add_cog(Report(bot))
