from discord.ext import commands, tasks
from datetime import datetime
import discord
import littxlecord
from discord.commands import slash_command, SlashCommandGroup


class BirthdayDB(littxlecord.DBHandler):
    def __init__(self):
        super().__init__("birthdays.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS birthdays (
             user_id INTEGER PRIMARY KEY,
             birth_date TEXT,
             guild_id INTEGER,
             channel_id INTEGER
            )"""
        )

    async def add_birthday(self, user_id, birth_date, guild_id, channel_id):
        await self.execute(
            "INSERT OR REPLACE INTO birthdays VALUES (?, ?, ?, ?)",
            (user_id, str(birth_date), guild_id, channel_id),
        )

    async def get_birthday_channel(self, guild_id):
        result = await self.fetchrow(
            "SELECT channel_id FROM birthdays WHERE guild_id = ?", (guild_id,)
        )
        return result["channel_id"] if result else None

    async def check_birthdays(self, today):
        return await self.fetchall(
            "SELECT user_id FROM birthdays WHERE substr(birth_date, 6) = ?", (today,)
        )


db = BirthdayDB()


class BirthdayCog(littxlecord.Cog, emoji="🎂"):
    birthday = SlashCommandGroup(
        "birthday", description="Schreiben Sie dort Ihren Geburtstag!🎂"
    )

    @birthday.command(description="Dein Geburtstag Tag!")
    async def set(self, ctx):
        modal = TutorialModal(title="Erstelle dein Geburtstag 🎂")
        await ctx.send_modal(modal)

    @birthday.command(
        description="Geben Sie den Kanal ein, in den der Bot schreiben soll, wenn jemand Geburtstag hat!"
    )
    async def birthday_channel(self, ctx, channel: discord.TextChannel):
        await db.add_birthday(ctx.author.id, None, ctx.guild.id, channel.id)
        month_day = datetime.today().strftime("%b %d")
        response = f"Dein Geburtstag am {month_day} wurde gespeichert ✅"
        await ctx.respond(response)


class TutorialModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Tag",
                placeholder="1-31",
                min_length=1,
                max_length=2,
            ),
            discord.ui.InputText(
                label="Monat",
                placeholder="1-12",
                min_length=1,
                max_length=2,
                style=discord.InputTextStyle.long,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction):
        try:
            day = int(self.children[0].value)
            month = int(self.children[1].value)

            if not (1 <= day <= 31 and 1 <= month <= 12):
                await interaction.response.send_message(
                    "Ungültiges Datumsformat. Verwende das Format MM-DD."
                )
                return self.stop()  # Stoppt die Interaktion und deaktiviert den Button

            birth_date = datetime(month=month, day=day)

        except (ValueError, TypeError):
            await interaction.response.send_message(
                "Ungültiges Datumsformat. Verwende das Format MM-DD."
            )
            return self.stop()  # Stoppt die Interaktion und deaktiviert den Button

        await interaction.guild.me.edit(
            birthdays=interaction.user.id, birth_date=birth_date
        )
        month_day = birth_date.strftime("%b %d")
        response = f"Dein Geburtstag am {month_day} wurde gespeichert ✅"
        await interaction.response.send_message(response)
        self.stop()


class TutorialView(discord.ui.View):
    @discord.ui.button(label="Klicke hier")
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(
            TutorialModal(title="Erstelle Dein Geburtstag")
        )

    @tasks.loop(hours=24)
    async def check_birthdays(self):
        today = datetime.today().strftime("%m-%d")
        users = await db.check_birthdays(today)

        for user_id in users:
            user = self.bot.get_user(user_id)
            if user:
                channel_id = await db.get_birthday_channel(user.guild.id)
                if channel_id:
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        await channel.send(
                            f"Alles Gute zum Geburtstag, {user.mention}! 🎉🎂"
                        )

    async def get_birthday_channel(self, guild_id):
        return await db.get_birthday_channel(guild_id)


def setup(bot):
    bot.add_cog(BirthdayCog(bot))
