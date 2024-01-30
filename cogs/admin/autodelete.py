import sqlite3
from discord.ext import commands, tasks
import discord
import datetime
from discord.commands import slash_command


class AutoDeleteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_connection = sqlite3.connect("data/db//autodelete.db")
        self.db_cursor = self.db_connection.cursor()
        self.wartezeit = None
        self.create_table()
        self.load_data()
        self.delete_messages.start()

    def create_table(self):
        self.db_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS autodelete (
                guild_id INTEGER,
                channel_id INTEGER,
                interval TEXT,  -- Füge eine Spalte für die Zeitangabe hinzu
                PRIMARY KEY (guild_id, channel_id)
            )
        """
        )

        self.db_connection.commit()

    def load_data(self):
        self.db_cursor.execute("SELECT * FROM autodelete")
        rows = self.db_cursor.fetchall()
        for row in rows:
            guild_id, channel_id, interval = row

    @slash_command()
    @discord.guild_only()
    @commands.has_permissions(manage_channels=True)
    @discord.default_permissions(manage_channels=True)
    async def autodelete(self, ctx, channel: discord.TextChannel, zeit: str):
        if not channel.permissions_for(ctx.guild.me).manage_messages:
            await ctx.respond(
                "Ich habe keine Berechtigung, Nachrichten in diesen Kanal zu verwalten",
                ephemeral=True,
            )
            return

        zeit = zeit.lower()
        einheit = zeit[-1]
        zeit = int(zeit[:-1])

        if einheit == "s":
            wartezeit = zeit
            einheit_text = "Sekunde(n)"
            einheit_text2 = "s"
        elif einheit == "m":
            wartezeit = zeit * 60
            einheit_text = "Minute(n)"
            einheit_text2 = "m"
        elif einheit == "h":
            wartezeit = zeit * 3600
            einheit_text = "Stunde(n)"
            einheit_text2 = "h"
        elif einheit == "d":
            wartezeit = zeit * 86400
            einheit_text = "Tag(e)"
            einheit_text2 = "d"
        else:
            await ctx.respond(
                "Ungültige Zeitangabe. Bitte verwende 's' für Sekunden, 'm' für Minuten oder 'h' für Stunden.",
                ephemeral=True,
            )
            return

        await ctx.respond(
            f"Nachrichten werden in {channel.mention} automatisch gelöscht nach {zeit} {einheit_text}."
        )

        # Speichere die Informationen für das automatische Löschen in der Datenbank
        autodelete_data = (
            ctx.guild.id,
            channel.id,
            f"{zeit}{einheit_text2}",
        )  # Füge die Zeitangabe mit dem Text hinzu
        self.db_cursor.execute(
            "INSERT OR REPLACE INTO autodelete VALUES (?, ?, ?)", autodelete_data
        )
        self.db_connection.commit()

        # Lade alle Einträge für das automatische Löschen aus der Datenbank
        self.db_cursor.execute("SELECT * FROM autodelete")
        all_autodelete_entries = self.db_cursor.fetchall()

        self.delete_messages.change_interval(seconds=wartezeit)

    @tasks.loop(seconds=1)  # Setzen Sie das Intervall auf 1 Sekunde oder nach Bedarf
    async def delete_messages(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                autodelete_data = self.db_cursor.execute(
                    "SELECT * FROM autodelete WHERE guild_id = ? AND channel_id = ?",
                    (guild.id, channel.id),
                ).fetchone()
                if autodelete_data:
                    messages = await channel.history(limit=None).flatten()
                    for message in messages[::-1]:
                        if not message.pinned:
                            await message.delete()
                            break

    @slash_command()
    @commands.has_permissions(manage_channels=True)
    @discord.default_permissions(manage_channels=True)
    async def autodelete_remove(self, ctx, channel: discord.TextChannel):
        self.db_cursor.execute(
            "DELETE FROM autodelete WHERE guild_id = ? AND channel_id = ?",
            (ctx.guild.id, channel.id),
        )
        self.db_connection.commit()
        await ctx.respond(
            f"Das automatische Löschen für {channel.mention} wurde entfernt."
        )


def setup(bot):
    bot.add_cog(AutoDeleteCog(bot))
