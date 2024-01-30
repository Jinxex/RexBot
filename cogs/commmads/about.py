import discord
import ezcord
import random

import pygount
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import datetime

start_time = datetime.datetime.now()




class FlexiiThisBot(ezcord.Cog):
    info = SlashCommandGroup("info")

    @info.command(description="🤖・Zeige Informationen über diesen Bot")
    async def bot(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="🍪 Hey du!",
            description=f"Hier findest du einige hilfreiche Informationen über mich - Falls du einen Bug findest, benutze bitte **{self.bot.get_cmd('bug')}** um diesen zu melden"
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar)
        embed.add_field(name="🌀 Server", value=f"```yaml\n{len(self.bot.guilds)}```", inline=True)
        embed.add_field(name="👥 Nutzer", value=f"```yaml\n{len(self.bot.users)}```", inline=True)
        embed.add_field(name="⌚ Uptime", value=f"```yaml\n🗓️ {start_time.strftime('%d.%m.%Y')}\n⏰ {start_time.strftime('%H:%M')}\n```", inline=False)

        await ctx.respond(embed=embed)

def setup(bot: discord.Bot):
    bot.add_cog(FlexiiThisBot(bot))