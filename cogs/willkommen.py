import discord
import aiosqlite
from discord.commands import slash_command, Option
from discord.ext import commands


class WelcomeCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DB = "welcome.db"

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                """CREATE TABLE IF NOT EXISTS welcome (
                    guild_id INTEGER,
                    welcome_channel INTEGER
                )"""
            )

    @slash_command()
    async def welcome_setup(
        self, ctx: discord.ApplicationContext, channel: Option(discord.TextChannel)
    ):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute(
                "SELECT * FROM welcome WHERE guild_id = ?", (ctx.guild.id,)
            )
            entry = await cursor.fetchone()

            if not entry:
                await db.execute(
                    "INSERT INTO welcome VALUES (?,?)", (ctx.guild.id, channel.id)
                )
            else:
                await db.execute(
                    "UPDATE welcome SET welcome_channel = ? WHERE guild_id = ?",
                    (channel.id, ctx.guild.id),
                )

            await db.commit()
            await ctx.respond(f"✅ Welcome channel set to {channel.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute(
                "SELECT * FROM welcome WHERE guild_id = ?", (member.guild.id,)
            )
            entry = await cursor.fetchone()

            if entry:
                channel_id = entry[1]
                channel = self.bot.get_channel(channel_id)

                if channel:
                    embed = discord.Embed(
                        description=f"Hey {member.mention} und herzlich willkommen auf dem Discord-Server von **{member.guild.name}!**\n\n\n★ Du bist das {member.guild.member_count} Mitglied auf diesem Server!",
                        color=discord.Color.red(),
                    )
                    embed.set_author(
                        icon_url=member.guild.icon.url, name=member.guild.name
                    )
                    embed.set_image(
                        url="https://tse4.mm.bing.net/th?id=OIP.zMe7JYEU-Rgv3G9prVh8CQHaCX&pid=Api&P=0&h=180"
                    )

                    await channel.send(member.mention, embed=embed)


def setup(bot):
    bot.add_cog(WelcomeCard(bot))
