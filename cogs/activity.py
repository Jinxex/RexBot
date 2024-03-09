import discord 
from discord.ext import commands
import asyncio
from discord.ext import tasks

class Activity(commands.Cog):
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
            activity3 = discord.CustomActivity(name=f"🌳 × Already on {server_count} servers")
            activity4 = discord.CustomActivity(name=f"🐱‍🐉 × Watching over {total_member_count} members")
            await self.bot.change_presence(activity=activity1)
            await asyncio.sleep(2)
            await self.bot.change_presence(activity=activity2)
            await asyncio.sleep(2)
            await self.bot.change_presence(activity=activity3)
            await asyncio.sleep(2)
            await self.bot.change_presence(activity=activity4)

def setup(bot):
    bot.add_cog(Activity(bot))
