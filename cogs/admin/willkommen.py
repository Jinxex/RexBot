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
            await ctx.respond(f"✅ Welcome channel set to {channel.mention}", ephemeral=True)

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
                        url="https://media.discordapp.net/attachments/1190258623511789603/1192734854073299095/dy1QM5M.png?ex=65aa27e5&is=6597b2e5&hm=480032919b01d512a06c30e4319680ef2f0b2dbbb3af1b4047dc7e5a09fc3957&=&format=webp&quality=lossless&width=1246&height=701"
                    )

                    await channel.send(member.mention, embed=embed)


def setup(bot):
    bot.add_cog(WelcomeCard(bot))
