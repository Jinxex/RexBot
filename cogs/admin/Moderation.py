import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import ezcord


class Moderation(ezcord.Cog, emoji="<a:moderator:1210988740613374013>"):



    Moderation = SlashCommandGroup("Moderation", description="Moderation commands")
    

    @Moderation.command(description="kick a user from server!")
    @discord.default_permissions(kick_members=True)
    @discord.guild_only()
    @discord.guild_only()
    async def kick(self, ctx, user: Option(discord.Member, "Select a user")):
        try:
            await user.kick()
        except discord.Forbidden:
            await ctx.respond("I do not have permission to kick this member")
            return
        await ctx.respond(f"{user.mention} got kicked!", ephemeral=True)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        await ctx.respond(f"An error has occurred: {error}")
        raise error


def setup(bot):
    bot.add_cog(Moderation(bot))

        