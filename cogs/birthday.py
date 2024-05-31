import asyncio

import discord
from discord.ext import commands, tasks
import ezcord
import os
import datetime
from discord.commands import SlashCommandGroup
import random

class BirthdayDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("database/birthday.db")

    async def setup(self):
        try:
            await self.execute(
                """CREATE TABLE IF NOT EXISTS birthdays(
                user_id INTEGER PRIMARY KEY,
                server_id INTEGER DEFAULT 0,
                birthday_channel_id INTEGER DEFAULT 0,
                birthday_role_id INTEGER DEFAULT 0,
                birthday_day INTEGER DEFAULT 0,
                birthday_month INTEGER DEFAULT 0
                )"""
            )
        except Exception as e:
            print(f"Error setting up database: {e}")

    async def set_birthday_channel(self, server_id, channel_id, role_id):
        await self.execute(
            "INSERT OR REPLACE INTO birthdays (server_id, birthday_channel_id, birthday_role_id) VALUES (?, ?, ?)",
            (server_id, channel_id, role_id)
        )

    async def get_birthday_channel(self, server_id):
        return await self.one(
            "SELECT birthday_channel_id FROM birthdays WHERE server_id = ?",
            (server_id,)
        )

    async def get_birthday_role(self, server_id):
        return await self.one(
            "SELECT birthday_role_id FROM birthdays WHERE server_id = ?",
            (server_id,)
        )

    async def get_server(self, server_id):
        return await self.one(
            "SELECT server_id FROM birthdays WHERE server_id = ?",
            (server_id,)
        )

    async def set_birthday_date(self, server_id, user_id, day, month):
        await self.execute(
            "INSERT OR REPLACE INTO birthdays (user_id, server_id, birthday_day, birthday_month) VALUES (?, ?, ?, ?)",
            (user_id, server_id, day, month)
        )

    async def get_birthday_date(self, day, month):
        return await self.one(
            "SELECT * FROM birthdays WHERE birthday_day = ? AND birthday_month = ?",
            (day, month)
        )



db = BirthdayDB()


options = [
    discord.SelectOption(label="All Servers", description="Receive congratulations on all servers", emoji="👑"),
    discord.SelectOption(label="Add This Server", description="The current servers can congratulate you", emoji="🎂"),
    discord.SelectOption(label="Remove This Server",
                         description="I no longer receive congratulations from these servers", emoji="⛔")
]


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_birthday.start()

    @ezcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(addbirthday())
        self.bot.add_view(changedate())
        self.bot.add_view(AttitudeView())

    @tasks.loop(hours=24)
    async def check_birthday(self):
        now = datetime.datetime.now()
        for guild in self.bot.guilds:
            today_birthdays = await db.get_birthday_date(now.day, now.month)

            if today_birthdays is None:
                print("No birthdays found for today in guild:", guild.name)
                continue

            channel_id = await db.get_birthday_channel(guild.id)  # Fetching channel ID once per guild

            if channel_id is None:
                continue  # Skip to the next guild if no birthday channel is found

            # Ensure channel_id is a single ID
            if isinstance(channel_id, tuple):
                channel_id = channel_id[0]

            channel = guild.get_channel(channel_id)
            if not channel:
                print(f"Invalid channel ID {channel_id} for guild {guild.name}")
                continue

            file_path = os.path.join(os.getcwd(), "img", "birthday.jpeg")
            thumbnail_url = "attachment://birthday.jpeg"

            for user_id in today_birthdays:
                member = guild.get_member(user_id)
                if member:
                    next_birthday = datetime.datetime(now.year, now.month, now.day)
                    if next_birthday < now:
                        next_birthday = next_birthday.replace(year=now.year + 1)
                    else:
                        print("Next birthday is today.")
                    days_until_birthday = (next_birthday - now).days

                    embed = discord.Embed(
                        title="🎉 Happy Birthday! 🥳",
                        description=f"Let's celebrate with {member.mention}:",
                        color=discord.Color.gold()
                    )
                    embed.set_thumbnail(url=thumbnail_url)
                    embed.add_field(name="Next birthday in", value=f"{days_until_birthday} days", inline=False)

                    print("Sending birthday message to channel:", channel.name)  # New print statement
                    await channel.send(embed=embed, file=discord.File(file_path, "birthday.jpeg"))

                    # Add birthday role to the member
                    role_id = await db.get_birthday_role(guild.id)
                    if role_id is not None:
                        role = guild.get_role(role_id)
                        if role is not None:
                            await member.add_roles(role)
                            print(f"Added birthday role {role.name} to {member.display_name}")

                            # Schedule removal of the role after 24 hours
                            await asyncio.sleep(24 * 3600)  # 24 hours in seconds
                            await member.remove_roles(role)
                            print(f"Removed birthday role {role.name} from {member.display_name} after 24 hours")
                        else:
                            print(f"Birthday role with ID {role_id} not found on server {guild.name}")
                    else:
                        print(f"No birthday role found for server {guild.name}")

                else:
                    print(f"Member with ID {user_id} not found on server {guild.name}.")

    birthday = SlashCommandGroup("birthday", description="Birthday related commands")

    @birthday.command(description="Set up your birthday notifications.")
    async def setup(self, ctx, birthday_channel: discord.TextChannel, birthday_role: discord.Role):
        server_id = ctx.guild.id
        if await db.get_server(server_id):
            embed = discord.Embed(
                title="🎂 Birthday Setup",
                description="Birthday notifications are already set up for this server.\n stop stop you can do `/birthday come` at any time",
                color=discord.Color.orange()
            )
            await ctx.defer()
            await ctx.respond(embed=embed, ephemeral=True)
            return

        await db.set_birthday_channel(server_id, birthday_channel.id, birthday_role.id)

        embed = discord.Embed(
            title="🎉 Birthday Setup 🎂",
            description=f"You've set up your birthday notifications in {birthday_channel.mention} channel!\nYou'll receive special birthday wishes from us! Your birthday role is {birthday_role.mention}.",
            color=discord.Color.orange()
        )
        file_path = os.path.join(os.getcwd(), "img", "birthday.jpeg")
        embed.set_thumbnail(url="attachment://birthday.jpeg")
        await ctx.defer()
        await ctx.respond(embed=embed, file=discord.File(file_path, "birthday.jpeg"), ephemeral=True, delete_after=60)

    @birthday.command(description="Get your birthday notifications.")
    @commands.guild_only()
    async def come(self, ctx):
        server_id = ctx.guild.id
        if await db.get_server(server_id):
            embed = discord.Embed(
                title="🎂 Birthday come",
                description="Birthday notifications are already set up for this server.\n stop stop you can do `/birthday remove` at any time",
                color=discord.Color.orange()
            )
            await ctx.defer()
            await ctx.respond(embed=embed, ephemeral=True)
            return
        embed = discord.Embed(
            title="🎉 Birthday Setup 🎂",
            description="Click the button below to set up your birthday! Once set up, you'll receive special birthday wishes from us!",
            color=discord.Color.blurple()
        )
        file_path = os.path.join(os.getcwd(), "img", "birthday.jpeg")
        embed.set_thumbnail(url="attachment://birthday.jpeg")
        embed.add_field(name="Note:", value="This action is irreversible. Make sure you input your birthday correctly!")
        await ctx.respond(embed=embed, file=discord.File(file_path, "birthday.jpeg"), view=addbirthday(),
                          ephemeral=True, delete_after=60)

    @birthday.command(description="Remove your birthday notifications.")
    @commands.guild_only()
    async def remove(self, ctx):
        embed = discord.Embed(
            title="🎂 Remove Birthday Setup 🎉",
            description="Click the button below to remove or new your birthday setup.",
            color=discord.Color.red()
        )
        file_path = os.path.join(os.getcwd(), "img", "birthday.jpeg")
        embed.set_thumbnail(url="attachment://birthday.jpeg")
        embed.add_field(name="Note:", value="Once removed, you won't receive special birthday wishes.")
        await ctx.defer()
        await ctx.respond(embed=embed, file=discord.File(file_path, "birthday.jpeg"), view=birthdaybutton(),
                          ephemeral=True, delete_after=60)


def setup(bot):
    bot.add_cog(Birthday(bot))


class addbirthday(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="add birthday", style=discord.ButtonStyle.green, emoji="🎂", custom_id="add birthday")
    async def add(self, button, interaction):
        await interaction.response.send_modal(AddBirthdayModal())


class AddBirthdayModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Day",
                value="18",
                style=discord.InputTextStyle.long,
                custom_id="add_day",
                min_length=2,
                max_length=2,
            ),
            discord.ui.InputText(
                label="Month",
                value="04",
                style=discord.InputTextStyle.long,
                custom_id="add_month",
                min_length=2,
                max_length=2,
            ),
            title="Add your birthday",
        )

    async def callback(self, interaction: discord.Interaction):
        day_input = self.children[0].value
        month_input = self.children[1].value

        if not day_input or not month_input:
            embed = discord.Embed(
                title="Error",
                description="Please fill in both day and month.",
                color=discord.Color.red()
            )
        else:
            try:
                day = int(day_input)
                month = int(month_input)
                if not 1 <= day <= 31 or not 1 <= month <= 12:
                    raise ValueError

                user_id = interaction.user.id

                # Assuming server_id is not needed for user-specific birthdays
                server_id = None

                await db.set_birthday_date(server_id, user_id, day, month)

                embed = discord.Embed(
                    title="Successfully set up 🎉",
                    description=f"You've set your birthday as **{day}.{month}**. If you need to make changes, use `/remove birthday`.",
                    color=discord.Color.green()
                )
            except ValueError:
                embed = discord.Embed(
                    title="Error",
                    description="Please enter valid day and month values.",
                    color=discord.Color.red()
                )

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)


class changedate(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, row=1, custom_id="cancel")
    async def cancel(self, button, interaction):
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Change birthday", style=discord.ButtonStyle.red, row=1, custom_id="Change birthday")
    async def Change(self, button, interaction):
        await interaction.response.send_modal(ChangeBirthdayModal())


class ChangeBirthdayModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Day",
                value="18",
                style=discord.InputTextStyle.short,
                custom_id="change_day",
                min_length=2,
                max_length=2,
            ),
            discord.ui.InputText(
                label="Month",
                value="04",
                style=discord.InputTextStyle.short,
                custom_id="change_month",
                min_length=2,
                max_length=2,
            ),
            title="Change your birthday"
        )

    async def callback(self, interaction: discord.Interaction):
        day_input = self.children[0].value
        month_input = self.children[1].value

        if not day_input or not month_input:
            embed = discord.Embed(
                title="Error",
                description="Please fill in both day and month.",
                color=discord.Color.red()
            )
        else:
            try:
                day = int(day_input)
                month = int(month_input)
                if not 1 <= day <= 31 or not 1 <= month <= 12:
                    raise ValueError

                user_id = interaction.user.id

                # Assuming server_id is not needed for user-specific birthdays
                server_id = None

                await db.set_birthday_date(server_id, user_id, day, month)
                embed = discord.Embed(
                    title="Successfully set up 🎉",
                    description=f"You've set your birthday as **{day}.{month}**. If you need to make changes, use `/remove birthday`.",
                    color=discord.Color.green()
                )
            except ValueError:
                embed = discord.Embed(
                    title="Error",
                    description="Please enter valid day and month values.",
                    color=discord.Color.red()
                )

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=60)


class birthdaybutton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label="change date", style=discord.ButtonStyle.primary, custom_id="Datum ändern")
    async def datum(self, button, interaction):
        embed = discord.Embed(
            title="Warning ⚠️",
            description="you can change your birthday every **100 days**!",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=changedate(), ephemeral=True, delete_after=60)

    @discord.ui.button(label="Attitude", style=discord.ButtonStyle.gray, custom_id="Attitude")
    async def Attitude(self, button, interaction):
        embed = discord.Embed(
            title="birthday",
            description="Your birthday is currently displayed on **all servers**.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=AttitudeView(), ephemeral=True, delete_after=60)


class AttitudeView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="AttitudeView",
        min_values=1,
        max_values=2,
        placeholder="⚙ > choose a setting",
        options=options,
    )
    async def callback(self, interaction):
        await interaction.response.send_message(f"Du hast {self.values[0]} gewählt")












