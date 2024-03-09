from discord.commands import slash_command, Option, SlashCommandGroup
from discord.ext import commands
import ezcord
import discord
import random
import asyncio
from datetime import datetime


class SternDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("db/stern.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            stern INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            Konto INTEGER DEFAULT 0
            )"""
        )

    async def add_stern(self, user_id, stern=0):
        async with self.start() as cursor:
            await cursor.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,)
            )
            await cursor.execute(
                "UPDATE users SET stern = stern + ? WHERE user_id = ?", (stern, user_id)
            )

    async def subtract_stern(self, user_id, stern):
        await self.execute(
            "UPDATE users SET stern = CASE WHEN stern - ? < 0 THEN 0 ELSE stern - ? END WHERE user_id = ?",
            (stern, stern, user_id),
        )

    async def get_stern(self, user_id):
        return await self.one("SELECT stern FROM users WHERE user_id = ?", user_id) or 0

    async def get_streak(self, user_id):
        return (
                await self.one("SELECT streak FROM users WHERE user_id = ?", user_id) or 0
        )

    async def update_streak(self, user_id, streak):
        await self.execute(
            "UPDATE users SET streak = ? WHERE user_id = ?", (streak or 0, user_id)
        )

    async def reset_streak(self, user_id):
        await self.execute("UPDATE users SET streak = 0 WHERE user_id = ?", user_id)

    async def get_current_cash(self, user_id):
        return (
                await self.one("SELECT stern FROM users WHERE user_id = ?", user_id)
                or 0
        )

    async def check_streak(self, user_id):
        return (
                await self.one("SELECT streak FROM users WHERE user_id = ? AND streak > 0", user_id)
                or False
        )

    async def add_stern(self, user_id, stern=0, to_account=False):
        async with self.start() as cursor:
            await cursor.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,)
            )
            if to_account:
                await cursor.execute(
                    "UPDATE users SET Konto = Konto + ? WHERE user_id = ?",
                    (stern, user_id),
                )
            else:
                await cursor.execute(
                    "UPDATE users SET stern = stern + ? WHERE user_id = ?",
                    (stern, user_id),
                )

    async def get_konto(self, user_id):
        return await self.one("SELECT Konto FROM users WHERE user_id = ?", user_id) or 0

    async def update_konto(self, user_id, amount):
        await self.execute(
            "UPDATE users SET Konto = Konto - ? WHERE user_id = ?", (amount, user_id)
        )

    async def get_max_streak(self, user_id):
        return await self.one("SELECT MAX(streak) FROM users WHERE user_id = ?", user_id) or 0

    async def add_bonus_stern(self, user_id, bonus_stern):
        await self.execute(
            "UPDATE users SET stern = stern + ? WHERE user_id = ?", (bonus_stern, user_id)
        )


db = SternDB()


class Stern(ezcord.Cog, emoji="⭐"):
    stern = SlashCommandGroup("stern", description="Don't let anyone steal ⭐")

    @stern.command(description="Claim your daily reward")
    @discord.guild_only()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        user_id = ctx.user.id

        current_streak = await db.get_streak(user_id)
        current_stern = random.randint(1, 10)

        if current_stern > 0 and await db.check_streak(user_id):
            current_streak += 1
            await db.update_streak(user_id, current_streak)

            if current_streak >= 12:
                min_bonus_sterne = 10
                max_bonus_sterne = 30

                bonus_sterne = random.randint(min_bonus_sterne, max_bonus_sterne)

                await db.add_bonus_stern(user_id, bonus_sterne)

                current_stern += bonus_sterne
                message = f"Daily Sterns\nYou claimed **{current_stern - bonus_sterne}** sterns and received a bonus of **{bonus_sterne}** sterns! Yummy!\n\nStreak: {current_streak} Days + Streak Maintained - Bonus Sterns: {bonus_sterne}"
            else:
                message = f"Daily Sterns\nYou claimed **{current_stern}** sterns! Yummy!\n\nStreak: {current_streak} Days + Streak Maintained"
        else:
            await db.reset_streak(user_id)
            current_streak = 1
            await db.update_streak(user_id, current_streak)
            message = f"Daily Sterns\nYou claimed **{current_stern}** sterns! Yummy!\n\nStreak: {current_streak} Day - Streak Lost"

        total_stern = await db.get_stern(user_id)
        await db.add_stern(user_id, current_stern)
        await db.close()

        embed = discord.Embed(
            title="Daily Sterns",
            description=message,
            color=discord.Color.yellow()
        )
        embed.add_field(name=f"You now have {total_stern + current_stern} sterns ⭐", value=" ")
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.defer()
        await ctx.respond(embed=embed)

    @stern.command(description="Steal some sterns from another user")
    @commands.cooldown(1, 7200, commands.BucketType.user)
    @discord.guild_only()
    async def steal(self, ctx, member: Option(discord.Member)):
        required_stern = 20
        user_stern = await db.get_stern(ctx.author.id)
        if user_stern < required_stern:
            embed_not_enough_stern = discord.Embed(
                title="Not Enough Sterns!",
                description=f"You need at least {required_stern} sterns to use this command.",
                color=discord.Color.red(),
            )
            embed_not_enough_stern.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.respond(embed=embed_not_enough_stern, ephemeral=True)
            return

        if member.id == ctx.author.id:
            stolen_stern = random.randint(1, 30)
            total_stern_stealer = await db.get_stern(ctx.author.id)

            embed = discord.Embed(
                title="**Who stole the stars from the sky?**",
                description=f"You stole {stolen_stern} sterns from the sky and ate them all.\n\n",
                color=discord.Color.yellow(),
            )
            embed.add_field(name=f"You now have {total_stern_stealer - stolen_stern} sterns ⭐")
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if member.id == ctx.bot.user.id:
            stolen_stern = random.randint(1, 5)
            total_stern_stealer = await db.get_stern(ctx.author.id)

            embed = discord.Embed(
                title="**Pretty Brave!**",
                description=f"You tried to steal stars from the master of stars!\n\n"
                            f"Unfortunately, you got caught and have to pay a penalty of {stolen_stern} sterns.\n\n"
                            f"You have {total_stern_stealer - stolen_stern:.3f} sterns left.",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            await ctx.defer()
            await ctx.respond(embed=embed, ephemeral=True)
            return

    @stern.command(description="Transfer stern to your account")
    @discord.guild_only()
    async def account(self, ctx, amount: int):
        user_id = ctx.author.id

        current_stern = await db.get_stern(user_id)
        if amount <= 0 or amount > current_stern:
            await ctx.respond(
                "Invalid amount or not enough stern to transfer.",
                ephemeral=True,
            )
            return
        await db.subtract_stern(user_id, amount)
        await db.add_stern(user_id, amount, to_account=True)

        embed = discord.Embed(
            title="stern Transferred to Account!",
            description=f"You have successfully transferred {amount} sterns to your account!",
            color=discord.Color.yellow(),
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        await ctx.defer()
        await ctx.respond(embed=embed)

    @stern.command()
    async def balance(self, ctx, member: Option(discord.Member) = None):
        member = member or ctx.author
        user_id = member.id

        current_stern = await db.get_stern(user_id)
        Konto = await db.get_konto(user_id)
        streak = await db.get_streak(user_id)
        max_streak = await db.get_max_streak(user_id)

        embed_balance = discord.Embed(
            title=f"{member.name}'s Stern Balance",
            color=discord.Color.blue(),
        )
        embed_balance.add_field(name="⭐ Sterns", value=f"```{current_stern}```", inline=True)
        embed_balance.add_field(name="📈 Streak", value=f"```{streak}```", inline=True)
        embed_balance.add_field(
            name="📊 Max Streak",
            value=f"```{max_streak}```",
            inline=False
        )
        embed_balance.add_field(
            name="💰 Konto",
            value=f"```{Konto}```",
            inline=True
        )
        embed_balance.set_thumbnail(url=member.display_avatar.url)
        await ctx.defer()
        await ctx.respond(embed=embed_balance)


def setup(bot):
    bot.add_cog(Stern(bot))
