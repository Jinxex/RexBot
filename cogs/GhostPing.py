import discord
from discord.ext import commands, tasks
import asyncio
import ezcord
from discord.commands import SlashCommandGroup, slash_command
from datetime import datetime, timedelta
import aiosqlite


class GhostDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("database/ghost.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS ghost_ping(
            guild_id INTEGER PRIMARY KEY,
            status INTEGER DEFAULT 0
            )
            """
        )
        await self.execute(
            """CREATE TABLE IF NOT EXISTS afk_status(
            user_id INTEGER PRIMARY KEY,
            is_afk INTEGER DEFAULT 0,
            afk_until TEXT
            )
            """
        )

    async def check_bot_settings(self, guild_id):
        result = await self.one("SELECT * FROM ghost_ping WHERE guild_id = ?", (guild_id,))
        if result is None:
            await self.execute("INSERT INTO ghost_ping (guild_id, status) VALUES (?, ?)", (guild_id, 0))
            result = await self.one("SELECT * FROM ghost_ping WHERE guild_id = ?", (guild_id,))
        return {"guild_id": result[0], "status": result[1]} if result else None

    async def update_bot_settings(self, guild_id, status):
        await self.execute("UPDATE ghost_ping SET status = ? WHERE guild_id = ?", (status, guild_id))

    async def delete_bot_settings(self, guild_id):
        await self.execute("DELETE FROM ghost_ping WHERE guild_id = ?", (guild_id,))


    async def set_afk_channel(self, guild_id, channel_id):
        await self.execute("UPDATE ghost_ping SET channel_id = ? WHERE guild_id = ?", (channel_id, guild_id))

    async def get_channel_id(self, guild_id):
        result = await self.one("SELECT channel_id FROM ghost_ping WHERE guild_id = ?", (guild_id,))
        return result[0] if result else None
    async def set_afk_status(self, user_id, is_afk, afk_until):
        await self.execute(
            "INSERT INTO afk_status (user_id, is_afk, afk_until) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET is_afk = ?, afk_until = ?",
            (user_id, is_afk, afk_until, is_afk, afk_until))

    async def check_afk_status(self, user_id):
        result = await self.one("SELECT * FROM afk_status WHERE user_id = ?", (user_id,))
        return {"user_id": result[0], "is_afk": result[1], "afk_until": result[2]} if result else None








db = GhostDB()


class GhostPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ghost = SlashCommandGroup("ghost", default_member_permissions=discord.Permissions(administrator=True))


    ghost_afk = SlashCommandGroup("ghost_afk")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        try:
            check_settings = await db.check_bot_settings(guild_id=message.guild.id)

            if isinstance(message.channel, discord.DMChannel):
                return

            if message.author.bot:
                return

            if check_settings["status"] != 0:
                if message.mentions:
                    if len(message.mentions) < 3:
                        for m in message.mentions:
                            if m != message.author and not m.bot:
                                embed = discord.Embed(
                                    title=f"👻 | Ghost ping",
                                    description=f"**{m.mention}**, you were ghost pinged by {message.author.mention}.\n\n**Message:** {message.content}",
                                    color=discord.Color.red()
                                )
                                await message.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title=f"👻 | Ghost ping",
                            description=f"**{len(message.mentions)} Users** have been ghost pinged.\n\n**Message by {message.author.mention}:** {message.content}",
                            color=discord.Color.red()
                        )
                        await message.channel.send(embed=embed)
        except Exception as e:
            print(f"An error occurred: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.mentions:
            for mentioned_user in message.mentions:
                afk_status = await db.check_afk_status(mentioned_user.id)
                if afk_status and afk_status["is_afk"] == 1:
                    await message.delete()

                    embed = discord.Embed(
                        title="AFK-Benachrichtigung",
                        description=f"{mentioned_user.mention} ist derzeit AFK und kann nicht gepingt werden.",
                        color=discord.Color.red()
                    )
                    embed.add_field(
                        name="Benutzer, der gepingt hat:",
                        value=f"{message.author.mention}",
                        inline=False
                    )

                    await message.channel.send(content=f"{message.author.mention}", embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # Check if the user is in AFK status
        afk_status = await db.check_afk_status(message.author.id)
        if afk_status and afk_status["is_afk"] == 1:
            # Remove the user from AFK status
            await db.set_afk_status(message.author.id, 0, None)

            # Delete all data of the user from the database
            await db.execute("DELETE FROM afk_status WHERE user_id =?", (message.author.id,))

            # Notify the user that their AFK status has been removed
            embed = discord.Embed(
                title="AFK Status Removed",
                description=f"{message.author.mention}, your AFK status has been removed and all your data has been deleted because you sent a message.",
                color=discord.Color.green()
            )
            await message.channel.send(f"{message.author.mention} is no longer AFK.", embed=embed)

    @ghost.command(description="Enable or disable the ghost ping system!")
    async def settings(self, ctx: discord.ApplicationContext):
        await ctx.defer(ephemeral=True)
        check_settings = await db.check_bot_settings(guild_id=ctx.guild.id)

        emb = discord.Embed(
            title="👻 | Configure the anti ghost ping system",
            description=f"Currently, the anti ghost ping system is {'**enabled**' if check_settings['status'] == 0 else '**disabled**'}. To {'**turn it off**' if check_settings['status'] == 0 else '**turn it on**'}, press the button below.",
            color=discord.Colour.blurple()
        )
        emb.set_footer(icon_url=ctx.guild.icon, text=f"{ctx.guild.name}")
        await ctx.respond(embed=emb, view=GhostPingButtons(check_settings), ephemeral=True)

    @ghost.command(description="Disable the ghost ping system!")
    async def disable(self, ctx: discord.ApplicationContext):
        await db.delete_bot_settings(ctx.guild.id)
        emb = discord.Embed(
            title="👻 | Anti ghost ping system disabled",
            description="The anti ghost ping system has been successfully disabled. From now on, no messages will be sent when a user mentions someone and deletes the message.",
            color=discord.Colour.red()
        )
        await ctx.respond(embed=emb, ephemeral=True)



    @ghost_afk.command(description="Set your AFK status")
    async def set(self, ctx: discord.ApplicationContext, time: str, *, reason: str):
        afk_until = datetime.utcnow() + timedelta(minutes=int(time))
        await db.set_afk_status(ctx.author.id, 1, afk_until)

        emb = discord.Embed(
            title="👋 | AFK status set",
            description=f"Your AFK status has been set. You will be marked as AFK for the next {time} minutes.\n\n**Reason:** {reason}",
            color=discord.Colour.green()
        )
        await ctx.respond(embed=emb, ephemeral=True)


def setup(bot):
    bot.add_cog(GhostPing(bot))

class GhostPingButtons(discord.ui.View):
    def __init__(self, check_settings):
        super().__init__(timeout=None)
        self.check_settings = check_settings

    @discord.ui.button(label="Toggle Ghost ping system", style=discord.ButtonStyle.blurple,
                       custom_id="toggle_ghost_ping", row=1)
    async def toggle_ghost_ping(self, button, interaction):
        new_status = 0 if self.check_settings["status"] != 0 else 1
        await db.update_bot_settings(interaction.guild.id, new_status)

        emb = discord.Embed(
            title=f"👻 | You have successfully switched the ghost ping system {'**off**' if new_status != 0 else '**on**'}",
            description=f"The anti ghost ping system is now {'**disabled**' if new_status != 0 else '**enabled**'}. From now on, a message will be sent when a user mentions someone and deletes the message.",
            color=discord.Colour.green()
        )
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel_ghost_ping", row=1)
    async def cancel_ghost_ping(self, button, interaction: discord.Interaction):
        emb = discord.Embed(
            title="👻 | Anti ghost ping system configuration canceled",
            description="The setting was successfully canceled, but you can change the settings at any time.",
            color=discord.Colour.red()
        )
        await interaction.response.edit_message(embed=emb, view=None)



