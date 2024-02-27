import discord 
from discord.ext import commands
import asyncio
from discord.ext import tasks

class activity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_activity.start()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_activity()

    @tasks.loop(seconds=10)
    async def update_activity(self):
        if self.bot.is_ready():
            server_count = len(self.bot.guilds)
            total_member_count = sum(guild.member_count for guild in self.bot.guilds)

            activity1 = discord.CustomActivity(name="🦊 × Nico")
            activity2 = discord.CustomActivity(name="⚙ × Beta Phase")
            activity3 = discord.CustomActivity(name=f"🌳 × Bereits auf {server_count} Servern")
            activity4 = discord.CustomActivity(name=f"🐱‍🐉 × Wacht über {total_member_count} Member")
            await self.bot.change_presence(activity=activity1)
            await asyncio.sleep(2)
            await self.bot.change_presence(activity=activity2)
            await asyncio.sleep(2)
            await self.bot.change_presence(activity=activity3)
            await asyncio.sleep(2)
            await self.bot.change_presence(activity=activity4)

def setup(bot):
    bot.add_cog(activity(bot))