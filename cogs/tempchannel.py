import littxlecord
from discord.commands import slash_command




class tempchannel(littxlecord.Cog):



    @slash_command()
    async def tempchannel(self,ctx):
        await ctx.channel.send("test")
        await ctx.respond("tempchannel is da!", ephemeral=True)




def setup(bot):
    bot.add_cog(tempchannel(bot))