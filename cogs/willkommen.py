import datetime
import discord
import ezcord
import random
from discord.ext import commands
from discord.commands import SlashCommandGroup

class WelcomeDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("db/wlc.db")

    async def setup(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS servers (
        server_id INTEGER PRIMARY KEY,
        channel_id INTEGER DEFAULT 0,
        title TEXT,
        description TEXT,
        enabled TEXT DEFAULT Off,
        welcome_role INTEGER DEFAULT 0
        )
        """)

    async def add_welcome_role(self, server_id, role_id):
        await self.exec("UPDATE servers SET welcome_role = ? WHERE server_id = ?", role_id, server_id)

    async def get_welcome_role(self, server_id):
        return await self.one("SELECT welcome_role FROM servers WHERE server_id = ?", server_id)

    async def enable(self, server_id, channel_id, enabled):
        async with self.start() as cursor:
            await self.exec("INSERT OR IGNORE INTO servers (server_id) VALUES (?)", server_id)
            await self.exec("UPDATE servers SET channel_id = ? WHERE server_id = ?", channel_id, server_id)
            await self.exec("UPDATE servers SET enabled = ? WHERE server_id = ?", enabled, server_id)

    async def disable(self, server_id, enabled):
        async with self.start() as cursor:
            await self.exec("UPDATE servers SET enabled = ? WHERE server_id = ?", enabled, server_id)

    async def check_enabled(self, server_id):
        return await self.one("SELECT enabled FROM servers WHERE server_id = ?", server_id)

    async def channel_id(self, server_id):
        return await self.one("SELECT channel_id FROM servers WHERE server_id = ?", server_id)

    async def add_to_db(self, server_id):
        await self.exec("INSERT INTO servers (server_id) VALUES (?)", server_id)

    async def fix(self, server_id):
        await self.exec("INSERT OR IGNORE INTO servers (server_id) VALUES (?)", server_id)

db = WelcomeDB()

class WelcomeSystem(ezcord.Cog):
    welcome = SlashCommandGroup("welcome", default_member_permissions=discord.Permissions(administrator=True))

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
                    f"{member.mention} is now part of the crew!",
                    f"{member.mention} made the right decision!",
                    f"We warmly welcome {member.mention} to **{member.guild.name}**!"
                ]
                welcome_phrase = random.choice(welcome_phrases)
                timestamp = f"🗓️ On {datetime.datetime.now().strftime('%d.%m.%Y')} at {datetime.datetime.now().strftime('%H:%M')}"

                # Retrieve role from the database
                role_id = await db.get_welcome_role(server_id)

                if role_id:
                    role = member.guild.get_role(role_id)
                    if role:
                        await member.add_roles(role)

                embed = discord.Embed(
                    title=f"👋 Welcome {member.display_name}!",
                    description=welcome_phrase,
                    color=discord.Color.random()
                )
                embed.set_footer(text=timestamp)
                try:
                    embed.set_thumbnail(url=member.display_avatar)
                except:
                    pass

                await channel.send(embed=embed, content=member.mention)
            except:
                return
        elif status == "Off":
            return

    @welcome.command(description="👋・Enable the Welcome System")
    @discord.guild_only()
    async def setup(self, ctx, role: discord.Role):
            status = await db.fix(ctx.guild.id)
            if status == None:
                status = "Off"
            if status == "Off":
                embed = discord.Embed(
                    color=discord.Color.blue(),
                    title="👋 Welcome System",
                    description="Please select the channel in the **Channel-Select** where welcome messages should be sent"
                )
                try:
                    embed.set_thumbnail(url=ctx.guild.icon)
                except:
                    pass
                await db.add_welcome_role(ctx.guild.id, role.id)

                await ctx.respond(embed=embed, view=WlcChannelSelect(ctx, self.bot))
            else:
                await ctx.respond(
                    f"> **Please turn off the system first with {self.bot.get_cmd('welcome stop')} and then use this command again!**",
                    ephemeral=True)

    @welcome.command(description="👋・Disable the Welcome System")
    @discord.guild_only()
    async def stop(self, ctx: discord.ApplicationContext):
            await ctx.defer()
            check_enabled = await db.check_enabled(ctx.guild.id)
            if check_enabled == "On":
                await db.disable(ctx.guild.id, "Off")
                embed = discord.Embed(
                    title="👋 Welcome System",
                    description=f"**The Welcome System is now turned off!**\n\n"
                                f"Turn it on again with {self.bot.get_cmd('welcome setup')}",
                    color=discord.Color.brand_green()
                )
                try:
                    embed.set_thumbnail(url=ctx.guild.icon)
                except:
                    pass
            else:
                embed = discord.Embed(
                    title="👋 Welcome System",
                    description=f"**The Welcome System is already turned off!**\n\n"
                                f"Turn it on with {self.bot.get_cmd('welcome setup')}",
                    color=discord.Color.brand_red()
                )
                try:
                    embed.set_thumbnail(url=ctx.user.display_avatar)
                except:
                    pass
            await ctx.respond(embed=embed)

def setup(bot: discord.Bot):
    bot.add_cog(WelcomeSystem(bot))

class WlcChannelSelect(discord.ui.View):
    def __init__(self, ctx, bot):
        self.ctx = ctx
        self.bot = bot
        super().__init__(timeout=30, disable_on_timeout=True)

    @discord.ui.channel_select(
        placeholder="Make a selection",
        custom_id="ChannelSelect",
        min_values=1,
        max_values=1,
        channel_types=[discord.ChannelType.text]
    )
    async def channel_select(self, select, interaction: discord.Interaction):
        if self.ctx.user.id == interaction.user.id:
            embed = discord.Embed(
                title="👋 Welcome System",
                description=f"**The Welcome System is now activated!**\n\n"
                            f"Deactivate it again with {self.bot.get_cmd('welcome stop')}",
                color=discord.Color.brand_green()
            )
            await interaction.message.edit(embed=embed, view=None)
            await db.enable(server_id=interaction.guild.id, channel_id=select.values[0].id, enabled="On")
        else:
            await interaction.response.send_message("> **You are not authorized to use this view!**", ephemeral=True)
