import discord
from discord.ext import commands
import datetime
from discord.commands import slash_command

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    @slash_command(
        name='stats',
        description="Give the bot stats",
    )
    async def stats_command(self, ctx):
        Support = discord.ui.Button(label="Support Srver", url="https://discord.gg/8ew7Sw6Tzy")
        button = discord.ui.Button(label="Invite Me", url="https://discord.com/api/oauth2/authorize?client_id=1170449421796900925&permissions=12670091163894&scope=applications.commands+bot")
        view = discord.ui.View()
        view.add_item(button)
        view.add_item(Support)

        server_count = len(self.bot.guilds)
        member_count = sum(guild.member_count for guild in self.bot.guilds)
        latency = f"{round(self.bot.latency * 1000)}ms"
        uptime = self.get_uptime()

        bot_avatar_url = self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url

        embed = discord.Embed(
            color=0x3498db
        )
        embed.set_author(name=self.bot.user.name, icon_url=bot_avatar_url)
        embed.set_thumbnail(url=bot_avatar_url)

        embed.add_field(name='Server Numbers', value=server_count, inline=True)
        embed.add_field(name='Server Members', value=member_count, inline=True)
        embed.add_field(name='Latency', value=latency, inline=True)
        embed.add_field(name='Uptime', value=uptime, inline=True)
        timestamp = datetime.datetime.utcnow().strftime("%H:%M Uhr")
        embed.add_field(name='Bot ID', value=f"{self.bot.user.id} • Heute um {timestamp}", inline=False)

        await ctx.respond(embed=embed,view=view)

    def get_uptime(self):
        now = datetime.datetime.utcnow()
        uptime_timedelta = now - self.start_time
        hours, remainder = divmod(uptime_timedelta.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        hours = int(hours)
        if hours == 0:
            if minutes == 0:
                return f"``Letzter Neustart ``<a:cloudcord:1192914941842300978>`` {int(seconds)} Sekunden``"
            else:
                return f"``Letzter Neustart ``<a:cloudcord:1192914941842300978>`` {int(minutes)} Minuten``"
        else:
            return f"``Letzter Neustart ``<a:cloudcord:1192914941842300978>`` {hours} Stunden``"


def setup(bot):
    bot.add_cog(Stats(bot))
