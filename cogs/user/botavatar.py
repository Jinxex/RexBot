import discord
from discord.ext import commands
from discord.commands import slash_command

class Botavatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Change bot's avatar")
    async def botavatar(
        self, ctx, img: discord.Attachment
    ):
        await ctx.defer()
        data = await img.read()
        try:
            await ctx.bot.user.edit(avatar=data)
            embed = discord.Embed(
                title="Avatar Changed ✅",
                description="Avatar changed successfully.",
                color=discord.Color.green()
            )
            await ctx.respond(embed=embed)
        except discord.errors.HTTPException:
            await ctx.respond("❌ Failed to change avatar.")



def setup(bot):
    bot.add_cog(Botavatar(bot))
