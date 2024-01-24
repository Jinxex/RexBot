import discord
from discord.commands import slash_command, Option
import littxlecord
from discord.ext import commands


class BanDB(littxlecord.DBHandler):
    def __init__(self):
        super().__init__("database/ban.db")

    async def setup(self):
        await self.exec(
            f"""CREATE TABLE IF NOT EXISTS ban (
            user_id INTEGER PRIMARY KEY,
            reason TEXT,
            dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )

    async def add_ban(self, user_id: int, reason: str | None):
        await self.exec(
            f"INSERT INTO ban (user_id, reason) VALUES (?, ?)", (user_id, reason)
        )

    async def is_user_banned(self, user_id: int):
        result = await self.fetchrow(f"SELECT user_id FROM ban WHERE user_id = ?", (user_id,))
        return result is not None

db = BanDB()

class Ban(littxlecord.Cog):

    @slash_command()
    async def ban(self, ctx, member: Option(discord.User, name="user"), reason: Option(str, name="reason", required=False)):
        await db.add_ban(member.id, reason)
        await ctx.respond(f"Banning user {member.name} with reason: {reason}")

    @commands.before_invoke
    async def check_ban(self, ctx):
        if await db.is_user_banned(ctx.author.id):
            await ctx.respond("You are banned from using this bot.")
            raise commands.CommandCancel()

def setup(bot):
    bot.add_cog(Ban(bot))
