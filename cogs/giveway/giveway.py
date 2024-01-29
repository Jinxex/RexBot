import discord
from discord.ext import commands
from discord.commands import slash_command, Option, SlashCommandGroup
import asyncio
import ezcord
import aiosqlite
import random
import datetime


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = "giveaway.db"

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.db) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS giveaway(
                user_id INTEGER,
                giveaway_id INTEGER)
                """)

            await db.commit()


    @slash_command(name="giveaway", description="Start a giveaway")
    async def giveaway_start(self, ctx,
                       time: Option(int, "How long should the giveaway be in minutes?", min_value=1, max_value=1440)):
        modal = Modal(title="Create a giveaway", time=time)
        await ctx.send_modal(modal)




def setup(bot):
    bot.add_cog(Giveaway(bot))


class Modal(discord.ui.Modal):
    def __init__(self, time, *args, **kwargs):
        self.time = time
        super().__init__(
            discord.ui.InputText(
                label="Giveaway Theme",
                placeholder="Giveaway for nitro",
                min_length=1,
                max_length=100,
            ),
            discord.ui.InputText(
                label="Giveaway Description",
                placeholder="Description about a Giveaway for nitro",
                style=discord.InputTextStyle.long
            ),

            *args,
            **kwargs

        )

    async def callback(self, interaction):
        time = 60 * self.time
        embed = discord.Embed(title=self.children[0].value, description=self.children[1].value)
        embed.add_field(name="Participate", value="Click on the button below to join the giveaway.")
        embed.add_field(name="Ends in", value=ezcord.times.dc_timestamp(time, "R"), inline=False)
        embed.set_footer(text=f"Giveaway is hosted by {interaction.user.name}")
        b = datetime.datetime.now()
        await interaction.response.send_message("Started giveaway.",ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        await asyncio.sleep(1)
        msg2 = msg.id
        deleting = await interaction.channel.send(view=GvwButton(msg=msg2))
        await asyncio.sleep(time)
        teilnehmer = 0

        teilnehmer2 = 0
        async with aiosqlite.connect("giveaway.db") as db:
            async with db.execute(
                    """
                    SELECT user_id FROM giveaway
                    WHERE giveaway_id = ?
                    """, (msg.id,)) as cursor:
                trow = await cursor.fetchall()
                for row in trow:
                    teilnehmer += 1
                if teilnehmer < 2:
                    embed = discord.Embed(title="Giveaway canceled", description="Nobody joined the giveaway.",
                                            color=discord.Color.red())
                    n = datetime.datetime.now()
                    embed.add_field(name="Giveaway Informations",
                                        value=f"Hosted by {interaction.user.mention}\nStarted at {discord.utils.format_dt(b, 'R')}\nEnded at {discord.utils.format_dt(n, 'R')}\nGiveaway Time: {time / 60} minutes\nParticipants: {teilnehmer}")
                    await msg.edit(
                        content="",embed=embed, view=None)
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
                                title="Giveaway Won",
                                description=f"Congratulations <@{gewinner2}>, you won the Giveaway!",
                                colour=discord.Color.yellow()
                            )
                            n = datetime.datetime.now()
                            embed.add_field(name="Giveaway Informations",value=f"Hosted by {interaction.user.mention}\nStarted at {discord.utils.format_dt(b, 'R')}\nEnded at {discord.utils.format_dt(n, 'R')}\nGiveaway Time: {time / 60} minutes\nParticipants: {teilnehmer}")
                            embed.add_field(name="Time", value=f"{time / 60} minutes")
                            await interaction.channel.send(embed=embed)
                            embed2 = discord.Embed(title="Giveaway ended", description="See below!",
                                                   color=discord.Color.nitro_pink())
                            await deleting.delete()
                            await msg.edit(content=f"<@{gewinner2}>", embed=embed2, view=None)


class GvwButton(discord.ui.View):
    def __init__(self, msg):
        super().__init__(timeout=None)
        self.msg = msg

    @discord.ui.button(label="Join Giveaway", style=discord.ButtonStyle.green, custom_id="join_giveaway")
    async def button_callback(self, button, interaction):
        async with aiosqlite.connect("giveaway.db") as db:
            async with db.execute("SELECT user_id FROM giveaway WHERE giveaway_id = ? AND user_id = ?",
                                  (self.msg, interaction.user.id)) as cursor:
                ids = await cursor.fetchall()
                print(ids)
        if ids:

            await interaction.response.send_message("You already joined the Giveaway. Leave it?",
                                                    view=LeaveButton(msg=self.msg), ephemeral=True)
        else:
            await interaction.response.send_message("You joined the Giveaway!", ephemeral=True)
            async with aiosqlite.connect("giveaway.db") as db:
                await db.execute("""
                INSERT INTO giveaway(user_id, giveaway_id)
                VALUES (?,?)
                """, (interaction.user.id, self.msg))
                await db.commit()


class LeaveButton(discord.ui.View):
    def __init__(self, msg):
        super().__init__(timeout=None)
        self.msg = msg

    @discord.ui.button(label="Leave Giveaway", style=discord.ButtonStyle.red, custom_id="leave")
    async def button_callback(self, button, interaction):
        await interaction.response.send_message("Left Giveaway.", ephemeral=True)
        async with aiosqlite.connect("giveaway.db") as db:
            await db.execute("""
            DELETE FROM giveaway WHERE user_id = ? and giveaway_id = ?
            """, (interaction.user.id, self.msg))
            await db.commit()