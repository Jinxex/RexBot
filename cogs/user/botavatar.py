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
        if ctx.author.id != 817435791079768105:
            return await ctx.respond("❌ Only the bot owner can change the bot's avatar.", ephemeral=True )

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

    @botavatar.error
    async def botavatar_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.respond("❌ Failed to fetch image.")
        elif isinstance(error, commands.CommandOnCooldown):
            hours = round(error.retry_after / 3600, 1)
            embed = discord.Embed(
                title="Cooldown ⏳",
                description=f"This command is on cooldown. Please try again in {hours} hours.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Botavatar(bot))
