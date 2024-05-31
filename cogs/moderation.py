import discord
from discord import Embed, Color
from discord.commands import slash_command, Option
from discord.ext import commands

import aiosqlite
import datetime

import traceback


class ModerationSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect("mod_sys.db") as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS WarnList (
                warn_id INTEGER PRIMARY KEY,
                mod_id INTEGER,
                guild_id INTEGER,
                user_id INTEGER,
                warns INTEGER DEFAULT 0,
                warn_reason TEXT,
                warn_time TEXT
                )
                """
            )

    @slash_command(description="Kick a user from the server")
    @discord.default_permissions(kick_members=True)
    @discord.guild_only()
    async def kick(
            self,
            ctx,
            member: Option(discord.Member, "Select the user you want to kick", required=True),
            reason: Option(str, "Provide a reason for kicking the user", required=False,
                           default="No reason provided")
    ):

        kick_embed = discord.Embed(
            title=f"`✅` Kick {member.name}#{member.discriminator}",
            description=f"You have kicked the user {member.mention} from the server **{ctx.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        kick_embed.add_field(name="Moderator:", value=f"{ctx.author}", inline=False)
        kick_embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        kick_embed.set_author(name=f"{ctx.guild.name}", icon_url=member.avatar.url)
        kick_embed.set_thumbnail(url=member.avatar.url)
        kick_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                              icon_url=ctx.author.display_avatar)

        try:
            await member.kick(reason=reason)
        except (discord.Forbidden, discord.HTTPException) as e:

            error_embed = discord.Embed(
                title="`⚠️` Error",
                description=f"An error occurred.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            error_embed.add_field(name=f"An error occurred while kicking {member.mention}.",
                                  value=f"Please try again later.", inline=False)
            error_embed.add_field(name=f"Error Code:", value=f"```{e}```", inline=False)
            error_embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.author.display_avatar)
            error_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                   icon_url=ctx.author.display_avatar)

            print(e)
            await ctx.defer()
            await ctx.respond(embed=error_embed, ephemeral=True)
            return
        await ctx.defer()
        await ctx.respond(embed=kick_embed, ephemeral=False)

    @slash_command(description="Ban a user from the server")
    @discord.default_permissions(ban_members=True)
    @discord.guild_only()
    async def ban(
            self,
            ctx,
            member: Option(discord.Member, "Select the user you want to ban", required=True),
            reason: Option(str, "Provide a reason for banning the user", required=False,
                           default="No reason provided")
    ):

        ban_embed = discord.Embed(
            title=f"`✅` Ban {member.name}#{member.discriminator}",
            description=f"You have banned the user {member.mention} from the server **{ctx.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        ban_embed.add_field(name="Moderator:", value=f"{ctx.author}", inline=False)
        ban_embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        ban_embed.set_author(name=f"{ctx.guild.name}", icon_url=member.avatar.url)
        ban_embed.set_thumbnail(url=member.avatar.url)
        ban_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                             icon_url=ctx.author.display_avatar)

        try:
            await member.ban(reason=reason)
        except (discord.Forbidden, discord.HTTPException) as e:

            error_embed = discord.Embed(
                title="`⚠️` Error",
                description=f"An error occurred.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            error_embed.add_field(name=f"An error occurred while banning {member.mention}.",
                                  value=f"Please try again later.", inline=False)
            error_embed.add_field(name=f"Error Code:", value=f"```{e}```", inline=False)
            error_embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.author.display_avatar)
            error_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                   icon_url=ctx.author.display_avatar)

            print(e)
            await ctx.defer()
            await ctx.respond(embed=error_embed, ephemeral=True)
            return
        await ctx.defer()
        await ctx.respond(embed=ban_embed, ephemeral=False)

    @slash_command(description="Unban a user from the server")
    @discord.default_permissions(ban_members=True)
    @discord.guild_only()
    async def unban(
            self,
            ctx,
            member: Option(discord.Member, "Select the user you want to unban", required=True),
            reason: Option(str, "Provide a reason for unbanning the user", required=False,
                           default="No reason provided")
    ):

        unban_embed = discord.Embed(
            title=f"`✅` Unban {member.name}#{member.discriminator}",
            description=f"You have unbanned the user {member.mention} from the server **{ctx.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        unban_embed.add_field(name="Moderator:", value=f"{ctx.author}", inline=False)
        unban_embed.add_field(name="Reason:", value=f"{reason}", inline=False)
        unban_embed.set_author(name=f"{ctx.guild.name}", icon_url=member.avatar.url)
        unban_embed.set_thumbnail(url=member.avatar.url)
        unban_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                               icon_url=ctx.author.display_avatar)

        try:
            ban_entry = await ctx.guild.fetch_ban(member)
            await ctx.guild.unban(ban_entry.user, reason=reason)
        except (discord.Forbidden, discord.HTTPException) as e:

            error_embed = discord.Embed(
                title="`⚠️` Error",
                description=f"An error occurred.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            error_embed.add_field(name=f"An error occurred while unbanning {member.mention}.",
                                  value=f"Please try again later.", inline=False)
            error_embed.add_field(name=f"Error Code:", value=f"```{e}```", inline=False)
            error_embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.author.display_avatar)
            error_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                   icon_url=ctx.author.display_avatar)

            print(e)
            await ctx.defer()
            await ctx.respond(embed=error_embed, ephemeral=True)
            return
        await ctx.defer()
        await ctx.respond(embed=unban_embed, ephemeral=False)

    @slash_command(description="Warn a user from the server")
    @discord.default_permissions(kick_members=True)
    @discord.guild_only()
    async def warn(
            self,
            ctx,
            member: Option(discord.Member, "Select the user you want to warn", required=True),
            reason: Option(str, "Provide a reason for warning the user", required=False,
                           default="No reason provided")
    ):

        warn_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiosqlite.connect("mod_sys.db") as db:
            await db.execute(
                "INSERT INTO WarnList (user_id, guild_id, warns, warn_reason, mod_id, warn_time) VALUES (?, ?, ?, ?, ?, ?)",
                (member.id, ctx.guild.id, 1, reason, ctx.author.id, warn_time),
            )
            await db.commit()

            async with db.execute(
                    "SELECT warn_id FROM WarnList WHERE user_id = ? AND guild_id = ? ORDER BY warn_id DESC LIMIT 1",
                    (member.id, ctx.guild.id),
            ) as cursor:
                row = await cursor.fetchone()
                warn_id = row[0]

        warnUser_embed = discord.Embed(
            title="`⚠️` Warn",
            description=f"You have been warned on the server **{ctx.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        warnUser_embed.add_field(name="Moderator:", value=f"```{ctx.author}```", inline=False)
        warnUser_embed.add_field(name="Warn ID:", value=f"```{warn_id}```", inline=False)
        warnUser_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        warnUser_embed.set_author(name=f"{ctx.guild.name}", icon_url=member.avatar.url)
        warnUser_embed.set_thumbnail(url=member.avatar.url)
        warnUser_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                  icon_url=ctx.author.display_avatar)

        warn_embed = discord.Embed(
            title="`✅` Warn",
            description=f"You have warned the user {member.mention} on the server **{ctx.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        warn_embed.add_field(name="Moderator:", value=f"```{ctx.author}```", inline=False)
        warn_embed.add_field(name="Warn ID:", value=f"```{warn_id}```", inline=False)
        warn_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        warn_embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.user.avatar.url)
        warn_embed.set_thumbnail(url=member.avatar.url)
        warn_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                              icon_url=ctx.author.display_avatar)
        await ctx.defer()
        await member.send(embed=warnUser_embed)
        await ctx.defer()
        await ctx.respond(embed=warn_embed, ephemeral=False)

    @slash_command(description="Unwarn a user from the server")
    @discord.default_permissions(kick_members=True)
    @discord.guild_only()
    async def unwarn(
            self,
            ctx,
            member: Option(discord.Member, "Select the user you want to unwarn"),
            warn_id: Option(int, "Select the warn ID you want to revoke", required=True),
            reason: Option(str, "Provide a reason for unwarning the user", required=False,
                           default="No reason provided")
    ):

        unwarnUser_embed = discord.Embed(
            title="`🍀` Unwarn",
            description=f"A warn from you on the server **{ctx.guild.name}** has been revoked.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        unwarnUser_embed.add_field(name="Moderator:", value=f"```{ctx.author}```", inline=False)
        unwarnUser_embed.add_field(name="Warn ID:", value=f"```{warn_id}```", inline=False)
        unwarnUser_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        unwarnUser_embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.author.display_avatar)
        unwarnUser_embed.set_thumbnail(url=ctx.guild.icon)
        unwarnUser_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                    icon_url=ctx.author.display_avatar)

        unwarn_embed = discord.Embed(
            title=f"`✅` Unwarn",
            description=f"You have unwarned {member.mention} from the server **{ctx.guild.name}**.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        unwarn_embed.add_field(name="Moderator:", value=f"```{ctx.author}```", inline=False)
        unwarn_embed.add_field(name="Warn ID:", value=f"```{warn_id}```", inline=False)
        unwarn_embed.add_field(name="Reason:", value=f"```{reason}```", inline=False)
        unwarn_embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.author.display_avatar)
        unwarn_embed.set_thumbnail(url=member.avatar.url)
        unwarn_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                icon_url=ctx.author.display_avatar)

        async with aiosqlite.connect("mod_sys.db") as db:
            await db.execute(
                "DELETE FROM WarnList WHERE user_id = ? AND guild_id = ? AND warn_id = ?",
                (member.id, ctx.guild.id, warn_id)
            )
            await db.commit()
        await ctx.defer()
        await member.send(embed=unwarnUser_embed)
        await ctx.defer()
        await ctx.respond(embed=unwarn_embed, ephemeral=False)

    @slash_command(description="Show all warns of a user from the server")
    @discord.default_permissions(kick_members=True)
    @discord.guild_only()
    async def warnings(self, ctx, member: discord.Member):

        warns_info = []
        async with aiosqlite.connect("mod_sys.db") as db:
            async with db.execute(
                    "SELECT warn_id, mod_id, guild_id, user_id, warns, warn_reason, warn_time FROM WarnList WHERE user_id = ? AND guild_id = ?",
                    (member.id, ctx.guild.id)) as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    warn_id, mod_id, guild_id, user_id, warns, warn_reason, warn_time = row
                    warn_time = datetime.datetime.strptime(warn_time, '%Y-%m-%d %H:%M:%S')
                    warns_info.append(
                        f"**Warn-ID:** __{warn_id}__ | **Warn issued at:** {warn_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    warns_info.append(f"**Moderator:** <@{mod_id}> | **Mod-ID**: __{mod_id}__\n")
                    warns_info.append(f"**> Reason:**\n```{warn_reason}```")
                    warns_info.append("\n")

        if not warns_info:
            warnings_embed = discord.Embed(
                title="`⚠️` The user has no warns!",
                description=f"User: {member.mention}",
                color=discord.Color.red(),
            )
        else:
            warnings_embed = discord.Embed(
                title=f"`⚠️` Warn List {member.name}#{member.discriminator}",
                description=f"__**List of Warns**__",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
        warnings_embed.add_field(name="", value="".join(warns_info), inline=False)
        warnings_embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon)
        warnings_embed.set_thumbnail(url=member.avatar)
        warnings_embed.set_footer(text=f"{ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                  icon_url=ctx.author.display_avatar)

        await ctx.defer()
        await ctx.respond(embed=warnings_embed, ephemeral=False)

    @slash_command(description="Delete messages from the channel")
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount: Option(int, "Number of messages (min. 1 | max. 100)", required=True)):
        amount = amount + 1

        if amount > 101:
            error_embed = discord.Embed(
                title="`❌` Error!",
                description="`I cannot delete more than 100 messages!`",
                color=discord.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            error_embed.set_thumbnail(url=ctx.guild.icon)
            error_embed.set_footer(text=f"| {ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                   icon_url=ctx.author.display_avatar)
            error_embed.set_author(name=f"Purge | Moderation System", icon_url=ctx.author.display_avatar)
            await ctx.defer()

            await ctx.respond(embed=error_embed, delete_after=6, ephemeral=True)
        else:
            deleted = await ctx.channel.purge(limit=amount)

            success_embed = discord.Embed(
                title="`✅` Success!",
                description="**{}** `messages deleted!`".format(len(deleted)),
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            success_embed.set_thumbnail(url=ctx.guild.icon)
            success_embed.set_footer(text=f"| {ctx.bot.user.name}#{ctx.bot.user.discriminator}",
                                     icon_url=ctx.author.display_avatar)
            success_embed.set_author(name=f"Purge | Moderation System", icon_url=ctx.author.display_avatar)
            await ctx.defer()
            await ctx.respond(embed=success_embed, delete_after=3, ephemeral=True)


def setup(bot):
    bot.add_cog(ModerationSystem(bot))