import discord
from discord.ext import commands
from datetime import datetime
import random
from discord.commands import slash_command

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()

    @slash_command(
        name='stats',
        description="give me stats on the bot"
    )
    async def stats_command(self, ctx):
        Support = discord.ui.Button(label="Support Server", url="https://discord.gg/8ew7Sw6Tzy")
        button = discord.ui.Button(label="Invite Me", url="https://discord.com/api/oauth2/authorize?client_id=1170449421796900925&permissions=12670091163894&scope=applications.commands+bot")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(Support)

        server_count = len(self.bot.guilds)
        member_count = sum(guild.member_count for guild in self.bot.guilds)
        latency = f"{round(self.bot.latency * 1000)}ms"
        bot_avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url


        embed_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        embed = discord.Embed(
            color=embed_color 
        )
        embed.set_author(name=self.bot.user.name, icon_url=bot_avatar_url)
        embed.set_thumbnail(url=bot_avatar_url)

        embed.add_field(name='Server Numbers', value=server_count, inline=True)
        embed.add_field(name='Server Members', value=member_count, inline=True)
        embed.add_field(name='Latency', value=latency, inline=True)
        embed.add_field(name='Last Reboot <a:cloudcord:1192914941842300978> ', value= discord.utils.format_dt((self.start_time), "R"), inline=True)
        timestamp = datetime.now().strftime("%H:%M Uhr")
        embed.add_field(name='Bot ID', value=f"{self.bot.user.id} • Heute um {timestamp}", inline=False)

        await ctx.respond(embed=embed, view=view)
def setup(bot):
    bot.add_cog(Stats(bot))
