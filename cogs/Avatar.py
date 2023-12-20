import discord
from discord.ext import commands
from discord.commands import slash_command, Option
from datetime import timedelta
from discord import default_permissions

class avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='avatar', description="📱〢Zeigt dir dein Avatar oder das Avatar eines Members an!")
    async def avatar(self, ctx, member: Option(discord.Member, "Wähle einen Memeber", required=False)):
        if member is None:
            selber_embed = discord.Embed(
                title="`🖼️` | Hier dein Profilbild!",
                color=0x2f3136
            )
            selber_embed.set_image(url=ctx.user.avatar.url)
            selber_embed.set_footer(icon_url=self.bot.user.avatar.url, text="| Created by Dynamo Development")
            await ctx.respond(embed=selber_embed)
            return
        else:
            anderer_embed = discord.Embed(
                title=f"`🖼️` | Hier das Profilbild von `{member.name}` ",
                color=0x2f3136
            )
            anderer_embed.set_image(url=member.avatar.url)
            anderer_embed.set_footer(icon_url=self.bot.user.avatar.url, text="|  Created by Dynamo Development")
            await ctx.respond(embed=anderer_embed)




def setup(bot):
    bot.add_cog(avatar(bot))