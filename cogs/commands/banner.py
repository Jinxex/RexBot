import discord
from discord.commands import slash_command, Option
from discord.ext import commands
import ezcord

class Banner(ezcord.Cog, emoji="❓"):

    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="banner",
        description="📱〢Zeigt dir dein Banner oder das Banner eines Members an!",
    )
    @discord.guild_only()
    async def banner_user(self, ctx, member: Option(discord.Member, "Das Mitglied, dessen Banner du sehen möchtest.")): # type: ignore

        if member is None:
            member = ctx.author

        try:
            banner_user = await self.bot.fetch_user(member.id)
            embed = discord.Embed(title=f"Banner von {member}", color=0x7289da)
            embed.set_image(url=banner_user.banner.url)

            await ctx.respond(embed=embed)

        except AttributeError:
            await ctx.respond(f"{member.mention} hat kein Banner.):", ephemeral=True)

def setup(bot):
    bot.add_cog(Banner(bot))
