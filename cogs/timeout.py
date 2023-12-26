import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from datetime import timedelta


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="timeout", description="")
    @commands.has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx,
        member: Option(discord.Member, "Choose a member"),
        reason: Option(str, required=False),
        days: Option(int, max_value=27, default=0, required=False),
        hours: Option(int, default=0, required=False),
        minutes: Option(int, default=0, required=False),
        seconds: Option(int, default=0, required=False),
    ):
        if member.id == ctx.author.id:
            await ctx.respond("You can't timeout yourself!", ephemeral=True)
            return
        if member.guild_permissions.moderate_members:
            await ctx.respond(
                "You can't do this, the person is a moderator", ephemeral=True
            )
            return
        duration = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        if duration >= timedelta(days=28):
            await ctx.respond(
                "I can't timeout someone for more than 28 days", ephemeral=True
            )
            return
        if reason == None:
            await member.timeout_for(duration)
            embed = discord.Embed(
                title="Timeout",
                description=f"{member.mention} was timeout for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds by {ctx.author.mention}.",
                color=0xDF0101,
            )
            await ctx.respond(embed=embed)
        else:
            await member.timeout_for(duration, reason=reason)
            embed = discord.Embed(
                title="Timeout",
                description=f"{member.mention} was timeout for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds by {ctx.author.mention} for '{reason}' .",
                color=0xDF0101,
            )

            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Admin(bot))
