import discord
from discord.ext import commands
from discord.commands import slash_command
import sqlite3
import re
import asyncio

user_message_counts = {}


class Global(commands.Cog):
    def __init__(self, bot, db_connection):
        self.bot = bot
        self.db_connection = db_connection
        self.create_tables()

    def create_tables(self):
        with self.db_connection as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS servers (
                    server_id TEXT PRIMARY KEY,
                    anti_link_channel_id TEXT,
                    spam_channel_id TEXT,
                    sync_channel_id TEXT,
                    spam_limit INTEGER, 
                    spam_cooldown INTEGER 
                )
            """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_message_counts (
                    server_id TEXT,
                    user_id TEXT,
                    message_count INTEGER,
                    PRIMARY KEY (server_id, user_id),
                    FOREIGN KEY (server_id) REFERENCES servers(server_id)
                )
            """
            )
            connection.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        server_id = str(message.guild.id)
        with self.db_connection as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM servers WHERE server_id = ?", (server_id,))
            server_data = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM user_message_counts WHERE server_id = ? AND user_id = ?",
                (server_id, str(message.author.id)),
            )
            user_data = cursor.fetchone()

        if server_data:
            (
                anti_link_channel_id,
                spam_channel_id,
                sync_channel_id,
                spam_limit,
                spam_cooldown,
            ) = server_data[1:6]

            if re.search("(?P<url>https://[^\s]+)", message.content):
                if message.channel.id == int(anti_link_channel_id):
                    await message.delete()
                    await message.author.send(
                        ":warning:**Daher der Dynamo Chat Aktiv ist auf diesem Server können keine Links gesendet werden.**"
                    )
                    return

            if message.channel.id == int(spam_channel_id):
                if user_data and user_data[2] >= spam_limit:
                    await message.delete()
                    await message.author.send(
                        f":warning:**Du hast das Nachrichtenlimit erreicht. Bitte warte {spam_cooldown} Sekunden, bevor du es erneut sendest.**"
                    )
                    return

                if user_data:
                    cursor.execute(
                        "UPDATE user_message_counts SET message_count = ? WHERE server_id = ? AND user_id = ?",
                        (user_data[2] + 1, server_id, str(message.author.id)),
                    )
                else:
                    cursor.execute(
                        "INSERT INTO user_message_counts (server_id, user_id, message_count) VALUES (?, ?, ?)",
                        (server_id, str(message.author.id), 1),
                    )

            crown = (
                "👑 Serveradmin "
                if message.author.guild_permissions.administrator
                else ":bust_in_silhouette: Servermitglied "
            )
            crown2 = (
                "👑"
                if message.author.guild_permissions.administrator
                else ":6700member:"
            )

            embed = discord.Embed(
                title=f"Nachricht von {message.author}",
                description=f"""
                    <:c_:1186136709046485062> *{message.content}*
                    """,
                color=discord.Color.blue(),
            )
            embed.set_footer(text="Created by Cloud Development")
            embed.set_author(
                name=f"{crown} ▪ {message.author} ▪ {message.author.status.name.capitalize()}",
                url=message.author.jump_url,
                icon_url=message.author.avatar.url,
            ),
            embed.add_field(
                name="Informationen",
                value=f"<:c_:1186136709046485062> [Bot Invite](https://discord.com/api/oauth2/authorize?client_id=1170449421796900925&permissions=8&scope=applications.commands+bot)) ▪ [{message.author.guild}]({message.channel.jump_url})",
            )
            embed.set_thumbnail(url=message.author.guild.icon.url)
            embed.set_image(
                url="https://media.discordapp.net/attachments/1136974237530325053/1186129843897770024/c_logo.png?ex=65922080&is=657fab80&hm=c0cacbdd397b88b2c9970d0ea37627dc18e3c742b07e1aec1f39adfd9fe2cd25&=&format=webp&quality=lossless&width=701&height=701"
            )

            if message.channel.id != int(sync_channel_id):
                return
        else:
            for channel_id in sync_channel_id:
                channel = self.bot.get_channel(int(channel_id))
            if channel:
                try:
                    sent_message = await channel.send(embed=embed)
                except Exception as e:
                    print(f"Error sending message to channel {channel_id}: {e}")
                else:
                    await asyncio.sleep(1)
                    await sent_message.delete()

            else:
                print(f"Channel not found: {channel_id}")

    @slash_command(name="setup_server")
    async def setup_server(
        self,
        ctx,
        anti_link_channel: discord.TextChannel,
        spam_channel: discord.TextChannel,
        sync_channel: discord.TextChannel,
        spam_limit: int,
        spam_cooldown: int,
    ):
        server_id = str(ctx.guild.id)
        anti_link_channel_id = str(anti_link_channel.id)
        spam_channel_id = str(spam_channel.id)
        sync_channel_id = str(sync_channel.id)

        with self.db_connection as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO servers (server_id, anti_link_channel_id, spam_channel_id, sync_channel_id, spam_limit, spam_cooldown)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    server_id,
                    anti_link_channel_id,
                    spam_channel_id,
                    sync_channel_id,
                    spam_limit,
                    spam_cooldown,
                ),
            )
            connection.commit()

        await ctx.respond(
            f"Server erfolgreich eingerichtet!\nAnti-Link-Channel: {anti_link_channel.mention}\nSpam-Channel: {spam_channel.mention}\nSync-Channel: {sync_channel.mention}\nSpam-Limit: {spam_limit}\nSpam-Cooldown: {spam_cooldown}",
            ephemeral=True,
        )


def setup(bot):
    db_connection = sqlite3.connect("Global.db")
    bot.add_cog(Global(bot, db_connection))
