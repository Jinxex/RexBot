import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import asyncio
import ezcord
import aiosqlite
import random
import datetime
import re

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = "db/giveaway.db"

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.db) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS giveaway(
                user_id INTEGER,
                giveaway_id INTEGER)
                """)
            await db.commit()

    giveway = SlashCommandGroup("giveway")

    @giveway.command(description="Start a giveaway")
    async def start(self, ctx: discord.ApplicationContext, time: str, description="Example 10s, 10m, 10h, 10d"):
        modal = Modal(title="Create a giveaway", time=time)
        await ctx.send_modal(modal)







def setup(bot):
    bot.add_cog(Giveaway(bot))

class Modal(discord.ui.Modal):
    def __init__(self, time, *args, **kwargs):
        self.time = self.parse_duration(time)
        self.participants_count = 0
        super().__init__(
            discord.ui.InputText(
                label="🎉 Giveaway Theme",
                placeholder="Giveaway for nitro",
                min_length=1,
                max_length=100,
            ),
            discord.ui.InputText(
                label="📝 Giveaway Description",
                placeholder="Description about a Giveaway for nitro",
                style=discord.InputTextStyle.long
            ),
            *args,
            **kwargs
        )

    def parse_duration(self, duration_text):
        time_regex = re.match(r'(\d+)([smh]?)', duration_text.lower())
        if not time_regex:
            raise commands.BadArgument("Invalid duration format. Use numbers followed by 's' for seconds, 'm' for minutes, or 'h' for hours.")

        amount, unit = time_regex.groups()
        amount = int(amount)

        if unit == 's':
            return amount
        elif unit == 'm':
            return amount * 60
        elif unit == 'h':
            return amount * 3600
        elif unit == 'd':
            return amount * 86400
        else:
            raise commands.BadArgument("Invalid unit. Use 's' for seconds, 'm' for minutes, 'h' for hours, or 'd' for days.")

    async def callback(self, interaction):
        time = self.time
        embed = discord.Embed(title=self.children[0].value, description=self.children[1].value, color=discord.Color.gold())
        embed.add_field(name="👥 Participants", value=str(self.participants_count), inline=False)
        embed.add_field(name="⏰ Ends in", value=ezcord.times.dc_timestamp(time, "R"), inline=False)
        embed.set_footer(text=f"🎉 Giveaway hosted by {interaction.user.name}")
        b = datetime.datetime.now()
        await interaction.response.send_message("🎉 Started giveaway.", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        await asyncio.sleep(1)
        msg2 = msg.id
        deleting = await interaction.channel.send(view=GvwButton(msg=msg2, modal=self,time=time,msge=msg))
        await asyncio.sleep(time)
        teilnehmer = 0

        teilnehmer2 = 0
        async with aiosqlite.connect("db/giveaway.db") as db:
            async with db.execute(
                    """
                    SELECT user_id FROM giveaway
                    WHERE giveaway_id = ?
                    """, (msg.id,)) as cursor:
                trow = await cursor.fetchall()
                for row in trow:
                    teilnehmer += 1
                if teilnehmer < 2:
                    embed = discord.Embed(title="🚫 Giveaway canceled", description="Nobody joined the giveaway.", color=discord.Color.red())
                    n = datetime.datetime.now()
                    embed.add_field(name="🎉 Giveaway Informations",
                                    value=f"Hosted by {interaction.user.mention}\n 🛫• Started at {discord.utils.format_dt(b, 'R')}\n 🔚• Ended at {discord.utils.format_dt(n, 'R')}\n\n⭐• Participants: {teilnehmer}")
                    await msg.edit(content="", embed=embed, view=None)
                    await deleting.delete()
                else:
                    gewinner = random.randint(1, teilnehmer)

                    async with db.execute("SELECT user_id FROM giveaway WHERE giveaway_id = ?", (msg.id,)) as cursor:
                        grow = await cursor.fetchall()
                    for row in grow:
                        teilnehmer2 += 1
                        if gewinner == teilnehmer2:
                            gewinner2 = row[0]
                            embed = discord.Embed(
                                title="🎉 Giveaway Won",
                                description=f"🥳 Congratulations <@{gewinner2}>, you won the Giveaway!",
                                colour=discord.Color.green()
                            )
                            n = datetime.datetime.now()
                            embed.add_field(name="🎉 Giveaway Informations", value=f"Hosted by {interaction.user.mention}\n🛫 • Started at {discord.utils.format_dt(b, 'R')}\n 🔚• Ended at {discord.utils.format_dt(n, 'R')}\n\n⭐• Participants: {teilnehmer}")
                            gewinner_message = await interaction.channel.send(embed=embed)
                            embed2 = discord.Embed(title="🎉 Giveaway ended", description="👋• See below!", color=discord.Color.purple())
                            await deleting.delete()
                            await msg.edit(content=f"🎉 <@{gewinner2}>", embed=embed2, view=None)
                            await discord.utils.sleep_until(gewinner_message.created_at + datetime.timedelta(hours=48))
                            await gewinner_message.delete()


class GvwButton(discord.ui.View):
    def __init__(self, msg,msge, modal,time):
        super().__init__(timeout=None)
        self.msg2 = msge
        self.msg = msg
        self.modal = modal
        self.time = time

    @discord.ui.button(label="🎉 Join Giveaway", style=discord.ButtonStyle.green, custom_id="join_giveaway")
    async def button_callback(self, button, interaction:discord.Interaction):
        async with aiosqlite.connect("db/giveaway.db") as db:
            async with db.execute("SELECT user_id FROM giveaway WHERE giveaway_id = ? AND user_id = ?",
                                  (self.msg, interaction.user.id)) as cursor:
                ids = await cursor.fetchall()
        if ids:
            await interaction.response.send_message("🚫 You already joined the Giveaway. Leave it?", view=LeaveButton(msg=self.msg, modal=self.modal,msge=self.msg2,time=self.time), ephemeral=True)
        else:
            self.modal.participants_count += 1
            print(f"DEBUG: Participants count increased to {self.modal.participants_count}")
            embed = discord.Embed(title=self.modal.children[0].value, description=self.modal.children[1].value, color=discord.Color.gold())
            embed.add_field(name="👥 Participants", value=str(self.modal.participants_count), inline=False)
            embed.add_field(name="⏰ Ends in", value=ezcord.times.dc_timestamp(self.time, "R"), inline=False)
            embed.set_footer(text=f"🎉 Giveaway hosted by {interaction.user.name}")
            await self.msg2.edit(embed=embed, view=None)
            await interaction.response.send_message("🎉 You joined the Giveaway!", ephemeral=True)
            async with aiosqlite.connect("db/giveaway.db") as db:
                await db.execute("""
                INSERT INTO giveaway(user_id, giveaway_id)
                VALUES (?,?)
                """, (interaction.user.id, self.msg))
                await db.commit()
class LeaveButton(discord.ui.View):
    def __init__(self,msge, msg,time, modal):
        super().__init__(timeout=None)
        self.msg2 = msge
        self.msg = msg
        self.modal = modal
        self.time = time

    @discord.ui.button(label="🚫 Leave Giveaway", style=discord.ButtonStyle.red, custom_id="leave")
    async def button_callback(self, button, interaction):
        self.modal.participants_count -= 1
        embed = discord.Embed(title=self.modal.children[0].value, description=self.modal.children[1].value, color=discord.Color.gold())
        embed.add_field(name="👥 Participants", value=str(self.modal.participants_count), inline=False)
        embed.add_field(name="⏰ Ends in", value=ezcord.times.dc_timestamp(self.time, "R"), inline=False)
        embed.set_footer(text=f"🎉 Giveaway hosted by {interaction.user.name}")
        await self.msg2.edit(embed=embed, view=None)
        await interaction.response.send_message("🚫 Left Giveaway.", ephemeral=True)
        async with aiosqlite.connect("db/giveaway.db") as db:
            await db.execute("""
            DELETE FROM giveaway WHERE user_id = ? and giveaway_id = ?
            """, (interaction.user.id, self.msg))
            await db.commit()



