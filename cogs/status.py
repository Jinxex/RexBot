import discord

import ezcord
class Status(ezcord.Cog):


    @ezcord.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.change_presence(status=discord.Status.offline)

    @ezcord.Cog.listener()
    async def on_guild_join(self, guild):
        await self.bot.change_presence(status=discord.Status.online)

def setup(bot):
    bot.add_cog(Status(bot))
