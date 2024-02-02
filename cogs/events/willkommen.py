import datetime
import sqlite3
import discord
import ezcord
import random
from discord.ext import commands
from discord.commands import SlashCommandGroup
from utils.db import WelcomeDB

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

                # Hier wird die Rolle aus der Datenbank abgerufen
                role_id = await db.get_welcome_role(server_id)

                if role_id:
                    role = member.guild.get_role(role_id)
                    if role:
                        await member.add_roles(role)

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

                await channel.send(embed=embed, content=member.mention)
            except:
                return
        elif status == "Off":
            return



    @welcome.command(description="👋・Aktiviere das Willkommens-System")
    @discord.default_permissions(administrator=True)
    @discord.guild_only()
    async def setup(self, ctx, role: discord.Role):
        status = await db.fix(ctx.guild.id)
        if status == None:
            status = "Off"
        if status == "Off":
            embed = discord.Embed(
                color=discord.Color.blue(),
                title="👋 Willkommens-System",
                description="Wähle bitte im **Channel-Select** den Kanal aus, in welchen Willkommensnachrichten gesendet werden sollen"
            )
            try:
                embed.set_thumbnail(url=ctx.guild.icon)
            except:
                pass
            await db.add_welcome_role(ctx.guild.id, role.id)

            await ctx.respond(embed=embed, view=WlcChannelSelect(ctx, self.bot))
        else:
            await ctx.respond(
                f"> **Bitte schalte das System erst mit {self.bot.get_cmd('welcome stop')} aus, und nutze dann diesen Command erneut!**",
                ephemeral=True)

    @welcome.command(description="👋・Deaktiviere das Willkommens-System")
    @discord.default_permissions(administrator=True)
    @discord.guild_only()
    async def stop(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        check_enabled = await db.check_enabled(ctx.guild.id)
        if check_enabled == "On": 
            await db.disable(ctx.guild.id, "Off")
            embed = discord.Embed(
                title="👋 Willkommens-System",
                description=f"**Das Willkommens-System ist nun ausgeschaltet!**\n\n"
                            f"Aktiviere es wieder mit {self.bot.get_cmd('welcome setup')} ",
                color=discord.Color.brand_green()
            )
            try:
                embed.set_thumbnail(url=ctx.guild.icon)
            except:
                pass
        else:  
            embed = discord.Embed(
                title="👋 Willkommens-System",
                description=f"**Das Willkommens-System ist bereits ausgeschaltet!**\n\n"
                            f"Aktiviere es mit {self.bot.get_cmd('welcome setup')}",
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