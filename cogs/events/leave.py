import discord
import aiosqlite
from discord.commands import slash_command, Option
from discord.ext import commands

class LeaveCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DB = "db/leave.db"

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            async with aiosqlite.connect(self.DB) as db:
                await db.execute(
                    """CREATE TABLE IF NOT EXISTS leave (
                        guild_id INTEGER,
                        leave_channel INTEGER
                    )"""
                )
        except aiosqlite.Error as e:
            print(f"Error creating table: {e}")

    @slash_command()
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def leave(self, ctx: discord.ApplicationContext, channel: Option(discord.TextChannel)):
        try:
            async with aiosqlite.connect(self.DB) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO leave (guild_id, leave_channel) 
                    VALUES (?, ?)
                    """,
                    (ctx.guild.id, channel.id)
                )
                await db.commit()

                embed = discord.Embed(
                    description=f"Leaves channel set to {channel.mention}.",
                    color=discord.Color.green(),
                )
                await ctx.respond(embed=embed, ephemeral=True)
        except aiosqlite.Error as e:
            print(f"Error updating db: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        try:
            async with aiosqlite.connect(self.DB) as db:
                cursor = await db.execute(
                    "SELECT * FROM leave WHERE guild_id = ?", (member.guild.id,)
                )
                entry = await cursor.fetchone()

                if entry:
                    channel_id = entry[1]
                    channel = self.bot.get_channel(channel_id)

                    embed = discord.Embed(
                        description=f"Hey {member.mention}, wir bedauern es sehr, dass du uns verlassen hast. Hoffentlich sehen wir uns wieder!",
                        color=discord.Color.red(),
                    )
                    embed.set_author(
                        icon_url=member.guild.icon.url, name=member.guild.name
                    )
                    await channel.send(embed=embed)
        except aiosqlite.Error as e:
            print(f"Error querying db: {e}")

def setup(bot):
    bot.add_cog(LeaveCard(bot))
