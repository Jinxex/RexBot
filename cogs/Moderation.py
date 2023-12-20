import discord
from discord import Embed, Color
from discord.commands import slash_command, Option
import cloudcord
import datetime
import traceback

options = [
        discord.SelectOption(label="timeout", description="Geben Sie einem Benutzer eine Auszeit!", emoji="🤐"),
        discord.SelectOption(label="warn", description="Geben Sie eine Benutzerwarnung ein", emoji="😲"),
        discord.SelectOption(label="ban", description="ban ein user auf dem server (1 bis 7 tage)", emoji="🔨"),
        discord.SelectOption(label="kick", description="kick ein user aus dem server!", emoji="😭"),
    ]

class ModDB(cloudcord.DBHandler):
    def __init__(self):
        super().__init__("mod.db")

    async def setup(self):
        """Execute a single query."""
        await self.exec(
            """CREATE TABLE IF NOT EXISTS mod (
                warn_id INTEGER PRIMARY KEY,
                mod_id INTEGER,
                guild_id INTEGER,
                user_id INTEGER,
                warns INTEGER DEFAULT 0,
                warn_reason TEXT,
                warn_time TEXT,
                ban_id INTEGER PRIMARY KEY,
                bans INTEGER DEFAULT 0,
                ban_reason TEXT,
                ban_time TEXT,
                kick_id INTEGER PRIMARY KEY,
                kicks INTEGER DEFAULT 0,
                kick_reason TEXT,
                kick_time TEXT,
                timeout_id INTEGER PRIMARY KEY,
                timeouts INTEGER DEFAULT 0,
                timeout_reason TEXT,
                timeout_time TEXT
            )
            """
        )

    async def add_warn(self, mod_id: int, guild_id: int, user_id: int, reason: str | None, warn_time: str):
        await self.exec(
            f"INSERT INTO {self.db_name} (mod_id, guild_id, user_id, warns, warn_reason, warn_time) VALUES (?, ?, ?, ?, ?, ?)",
            (mod_id, guild_id, user_id, 1, reason, warn_time)
        )

    async def add_ban(self, mod_id: int, guild_id: int, user_id: int, reason: str | None, ban_time: str):
        await self.exec(
            f"INSERT INTO {self.db_name} (mod_id, guild_id, user_id, bans, ban_reason, ban_time) VALUES (?, ?, ?, ?, ?, ?)",
            (mod_id, guild_id, user_id, 1, reason, ban_time)
        )

    async def add_kick(self, mod_id: int, guild_id: int, user_id: int, reason: str ):
        await self.exec(
            f"INSERT INTO {self.db_name} (mod_id, guild_id, user_id, kicks, kick_reason, ) VALUES (?, ?, ?, ?, ?, ?)",
            (mod_id, guild_id, user_id, 1, reason)
        )

    async def add_timeout(self, mod_id: int, guild_id: int, user_id: int, reason: str | None, timeout_time: str):
        await self.exec(
            f"INSERT INTO {self.db_name} (mod_id, guild_id, user_id, timeouts, timeout_reason, timeout_time) VALUES (?, ?, ?, ?, ?, ?)",
            (mod_id, guild_id, user_id, 1, reason, timeout_time)
        )

class Mod(cloudcord.Cog, emoji="🌩"):

    @cloudcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(modView())

    @slash_command()
    async def mod(self, ctx):
        await ctx.respond("wieso hast du das gemacht", view=modView())


def setup(bot):
    bot.add_cog(Mod(bot))


class modView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        min_values=1,
        max_values=2,
        placeholder="Triff eine Auswahl",
        options=options,
        custom_id="timeout"
    )
    async def select_callback(self, select, interaction):
        if "timeout" in select.values:
            labels = [option.label for option in select.options]
            if "timeout" not in labels:
                select.append_option(TimeoutError)
            else:
                select.disabled = True

            await interaction.response.edit_message(view=self)
        else:
            s = ""
            for auswahl in select.values:
                s += f"- {auswahl}\n"

            await interaction.response.send_message(f"Du hast folgendes ausgewählt:\n{s}")