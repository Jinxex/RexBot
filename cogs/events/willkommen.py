import datetime

import discord
import ezcord
import random
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import emoji


class WelcomeDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("data/db/wlc.db")

    async def setup(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS servers (
        server_id INTEGER PRIMARY KEY,
        channel_id INTEGER DEFAULT 0,
        title TEXT,
        description TEXT,
        enabled TEXT DEFAULT Off
        )
        """)

    async def enable(self, server_id, channel_id, enabled):
        async with self.start() as cursor:
            await self.exec("INSERT OR IGNORE INTO servers (server_id) VALUES (?)", server_id)
            await self.exec("UPDATE servers SET channel_id = ? WHERE server_id = ?", channel_id, server_id)
            await self.exec("UPDATE servers SET enabled = ? WHERE server_id = ?", enabled, server_id)

    async def disable(self, server_id, enabled):
        await self.exec("UPDATE servers SET enabled = ? WHERE server_id = ?", enabled, server_id)

    async def check_enabled(self, server_id):
        return await self.one("SELECT enabled FROM servers WHERE server_id = ?", server_id)

    async def channel_id(self, server_id):
        return await self.one("SELECT channel_id FROM servers WHERE server_id = ?", server_id)

    async def add_to_db(self, server_id):
        await self.exec("INSERT INTO servers (server_id) VALUES (?)", server_id)

    async def fix(self, server_id):
        await self.exec("INSERT INTO servers (server_id) VALUES (?)", server_id,)

db = WelcomeDB()


class WelcomeSystem(ezcord.Cog):
    welcome = SlashCommandGroup("welcome")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        server_id = member.guild.id
        try:
            status = await db.check_enabled(server_id)
        except:
            return

        if status == "On":
            channel_id = await db.channel_id(server_id)
            try:
                channel = member.guild.get_channel(channel_id)
                welcome_phrases = [
                    f"{member.mention} gehört nun auch zur Crew!",
                    f"{member.mention} hat die richtige Entscheidung getroffen!",
                    f"Wir heißen {member.mention} herzlich auf **{member.guild.name}** willkommen!"
                ]
                welcome_phrase = random.choice(welcome_phrases)
                timestamp = f"🗓️ Am {datetime.datetime.now().strftime('%d.%m.%Y')} um {datetime.datetime.now().strftime('%H:%M')}"
                embed = discord.Embed(
                    title=f"👋 Willkommen {member.display_name}!",
                    description=welcome_phrase,
                    color=discord.Color.random()
                )
                embed.set_footer(text=timestamp)
                try:
                    embed.set_thumbnail(url=member.display_avatar)
                except:
                    pass
                ## TODO: Embed bearbeitbar in einem extra Menü
                await channel.send(embed=embed, content=member.mention)
            except:
                return
        elif status == "Off":
            return

    @welcome.command(description='fix')
    async def fix(self, ctx):
        await db.fix(ctx.guild.id)
        await ctx.respond('Fixed!')


    @welcome.command(description="👋・Aktiviere das Wilkommens-System")
    async def setup(self, ctx: discord.ApplicationContext):
        status = await db.check_enabled(ctx.guild.id)
        if status == "Off":
            embed = discord.Embed(
                color=emoji.color_blue,
                title="👋 Willkommens-System",
                description="Wähle bitte im **Channel-Select** den Kanal aus, in welchen Willkommensnachrichten gesendet werden sollen"
            )
            try:
                embed.set_thumbnail(url=ctx.guild.icon)
            except:
                pass
            await ctx.respond(embed=embed, view=WlcChannelSelect(ctx, self.bot))
        else:
            await ctx.respond(
                f"> **Bitte schalte das System erst mit {self.bot.get_cmd('welcome stop')} aus, und nutze dann diesen Command erneut!**",
                ephemeral=True)

    @welcome.command(description="👋・Deaktiviere das Willkommens-System")
    async def stop(self, ctx: discord.ApplicationContext):
        status = await db.check_enabled(ctx.guild.id)
        if status == "On":
            await db.disable(ctx.guild.id, "Off")
            embed = discord.Embed(
                title="👋 Willkommens-System",
                description=f"**Das Willkommens-System ist nun ausgeschaltet!**\n\n"
                            f"Aktiviere es wieder mit {self.bot.get_cmd('welcome setup')}",
                color=discord.Color.brand_green()
            )
            try:
                embed.set_thumbnail(url=ctx.user.display_avatar)
            except:
                await ctx.respond(embed=embed)
        elif status == "Off":
            embed = discord.Embed(
                title="👋 Willkommens-System",
                description=f"**Das Willkommens-System ist bereits ausgeschaltet!**\n\n"
                            f"Aktiviere es mit {self.bot.get_cmd('welcome setup')}",
                color=discord.Color.brand_red()
            )
            try:
                embed.set_thumbnail(url=ctx.user.display_avatar)
            except:
                await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(WelcomeSystem(bot))


class WlcChannelSelect(discord.ui.View):
    def __init__(self, ctx, bot):
        self.ctx = ctx
        self.bot = bot
        super().__init__(timeout=30, disable_on_timeout=True)

    @discord.ui.channel_select(
        placeholder="Triff eine Auswahl",
        custom_id="ChannelSelect",
        min_values=1,
        max_values=1,
        channel_types=[discord.ChannelType.text]
    )
    async def channel_select(self, select, interaction: discord.Interaction):
        if self.ctx.user.id == interaction.user.id:
            embed = discord.Embed(
                title="👋 Willkommens-System",
                description=f"**Das Willkommens-System ist nun aktiviert!**\n\n"
                            f"Deaktiviere es wieder mit {self.bot.get_cmd('welcome stop')}",
                color=discord.Color.brand_green()
            )
            await interaction.message.edit(embed=embed, view=None)
            await db.enable(server_id=interaction.guild.id, channel_id=select.values[0].id, enabled="On")

        else:
            await interaction.response.send_message("> **Du bist nicht berechtigt, diese View zu nutzen!**", ephemeral=True)