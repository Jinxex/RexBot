import discord
from discord.commands import SlashCommandGroup, Option
import ezcord







class automod(ezcord.Cog):





    automod= SlashCommandGroup("automod", description="mach dir das automod an ")




    @automod.command(description="aktivieren sie dem automod")
    async def setup(
        self,
        ctx,
    ):
        await ctx.respond("automod")



def setup(bot):
    bot.add_cog(automod(bot))
