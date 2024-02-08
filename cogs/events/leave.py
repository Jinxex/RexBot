import datetime
import discord
import ezcord
import random
from discord.ext import commands
from discord.commands import SlashCommandGroup


class leaveDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("db/wlc.db")

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

db = leaveDB()


class leaveSystem(ezcord.Cog):
    leave = SlashCommandGroup("leave")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        server_id = member.guild.id
        try:
            status = await db.check_enabled(server_id)
        except:
            return

        if status == "On":
            channel_id = await db.channel_id(server_id)
            try:
                channel = member.guild.get_channel(channel_id)
                leave_phrases = [
                    f"{member.mention} gehört nun nicht mehr zur Crew!",
                    f"{member.mention} lieder hast du uns verlassen",
                    f"wir wünschen dir{member.mention} noch viel Glück **{member.guild.name}** auf deinen Reise!"
                ]
                leave_phrase = random.choice(leave_phrases)
                timestamp = f"🗓️ Am {datetime.datetime.now().strftime('%d.%m.%Y')} um {datetime.datetime.now().strftime('%H:%M')}"


                embed = discord.Embed(
                    title=f"👋 leave {member.display_name}!",
                    description=leave_phrase,
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



    @leave.command(description="👋・Aktiviere das leaves-System")
    @discord.default_permissions(administrator=True)
    @discord.guild_only()
    async def setup(self, ctx):
        status = await db.fix(ctx.guild.id)
        if status == None:
            status = "Off"
        if status == "Off":
            embed = discord.Embed(
                color=discord.Color.blue(),
                title="👋 leaves-System",
                description="Wähle bitte im **Channel-Select** den Kanal aus, in welchen leavesnachrichten gesendet werden sollen"
            )
            try:
                embed.set_thumbnail(url=ctx.guild.icon)
            except:
                pass

            await ctx.respond(embed=embed, view=leaChannelSelect(ctx, self.bot))
        else:
            await ctx.respond(
                f"> **Bitte schalte das System erst mit {self.bot.get_cmd('leave stop')} aus, und nutze dann diesen Command erneut!**",
                ephemeral=True)

    @leave.command(description="👋・Deaktiviere das leaves-System")
    @discord.default_permissions(administrator=True)
    @discord.guild_only()
    async def stop(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        check_enabled = await db.check_enabled(ctx.guild.id)
        if check_enabled == "On": 
            await db.disable(ctx.guild.id, "Off")
            embed = discord.Embed(
                title="👋 leaves-System",
                description=f"**Das leaves-System ist nun ausgeschaltet!**\n\n"
                            f"Aktiviere es wieder mit {self.bot.get_cmd('leave setup')} ",
                color=discord.Color.brand_green()
            )
            try:
                embed.set_thumbnail(url=ctx.guild.icon)
            except:
                pass
        else:  
            embed = discord.Embed(
                title="👋 leaves-System",
                description=f"**Das leaves-System ist bereits ausgeschaltet!**\n\n"
                            f"Aktiviere es mit {self.bot.get_cmd('leave setup')}",
                color=discord.Color.brand_red()
            )
            try:
                embed.set_thumbnail(url=ctx.user.display_avatar)
            except:
                pass
        await ctx.respond(embed=embed)




def setup(bot: discord.Bot):
    bot.add_cog(leaveSystem(bot))


class leaChannelSelect(discord.ui.View):
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
                title="👋 leaves-System",
                description=f"**Das leaves-System ist nun aktiviert!**\n\n"
                            f"Deaktiviere es wieder mit {self.bot.get_cmd('leave stop')}",
                color=discord.Color.brand_green()
            )
            await interaction.message.edit(embed=embed, view=None)
            await db.enable(server_id=interaction.guild.id, channel_id=select.values[0].id, enabled="On")

        else:
            await interaction.response.send_message("> **Du bist nicht berechtigt, diese View zu nutzen!**", ephemeral=True)