import discord
import random
import littxlecord
from datetime import datetime, timezone

class leavesevent(littxlecord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @littxlecord.Cog.listener()
    async def on_guild_remove(self, guild):
        embed_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            kicked_by = entry.user
            kick_time = entry.created_at
            break
        else:
            kicked_by = "Unknown"
            kick_time = "Unknown"

        now = datetime.utcnow()
        bot_join_time = (now - guild.me.joined_at).days

        embed = discord.Embed(
            title="Vom Server entfernt :(",
            color=embed_color
        )
        embed.add_field(name="Server", value=guild.name, inline=False)
        embed.add_field(name="Bot wurde entfernt von", value=str(kicked_by), inline=False)
        embed.add_field(name="Wann", value=str(kick_time), inline=False)
        embed.add_field(name="Wie lange auf dem Server", value=f"{bot_join_time} Tage", inline=False)

        channel = self.bot.get_channel(1190258623511789602)
        if channel:
            await channel.send(embed=embed)
        else:
            print("Error: Channel not found")

def setup(bot):
    bot.add_cog(leavesevent(bot))
