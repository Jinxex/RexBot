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
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS giveaway(
                user_id INTEGER,
                giveaway_id INTEGER)
                """
            )

            await db.commit()

    @slash_command(name="giveaway", description="Starte ein Giveaway")
    async def giveaway_start(
        self,
        ctx,
        time: Option(
            int,
            "Wie lange soll das Giveaway dauern? (in Minuten)",
            min_value=1,
            max_value=1440,
        ),
    ):
        modal = Modal(title="Erstelle ein Giveaway", time=time)
        await ctx.send_modal(modal)


def setup(bot):
    bot.add_cog(Giveaway(bot))


class Modal(discord.ui.Modal):
    def __init__(self, time, *args, **kwargs):
        self.time = time
        super().__init__(
            discord.ui.InputText(
                label="Thema des Giveaways",
                placeholder="Giveaway für Nitro",
                min_length=1,
                max_length=100,
            ),
            discord.ui.InputText(
                label="Beschreibung des Giveaways",
                placeholder="Beschreibung für ein Nitro Giveaway",
                style=discord.InputTextStyle.long,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction):
        time = 60 * self.time
        embed = discord.Embed(
            title=self.children[0].value, description=self.children[1].value
        )
        embed.add_field(
            name="Teilnehmen",
            value="Klicke auf den Button unten, um am Giveaway teilzunehmen.",
        )
        embed.add_field(
            name="Endet in", value=ezcord.times.dc_timestamp(time, "R"), inline=False
        )
        embed.set_footer(text=f"Giveaway wird von {interaction.user.name} veranstaltet")
        b = datetime.datetime.now()
        await interaction.response.send_message("Giveaway gestartet.", ephemeral=True)
        msg = await interaction.channel.send(embed=embed)
        await asyncio.sleep(1)
        msg_id = msg.id
        deleting = await interaction.channel.send(view=GvwButton(msg=msg_id))
        await asyncio.sleep(time)
        teilnehmer = 0

        teilnehmer2 = 0
        async with aiosqlite.connect("giveaway.db") as db:
            async with db.execute(
                """
                    SELECT user_id FROM giveaway
                    WHERE giveaway_id = ?
                    """,
                (msg.id,),
            ) as cursor:
                trow = await cursor.fetchall()
                for row in trow:
                    teilnehmer += 1
                if teilnehmer < 2:
                    embed = discord.Embed(
                        title="Giveaway abgebrochen",
                        description="Niemand hat am Giveaway teilgenommen.",
                        color=discord.Color.red(),
                    )
                    n = datetime.datetime.now()
                    embed.add_field(
                        name="Giveaway Informationen",
                        value=f"Veranstaltet von {interaction.user.mention}\nGestartet um {discord.utils.format_dt(b, 'R')}\nBeendet um {discord.utils.format_dt(n, 'R')}\nDauer des Giveaways: {time / 60} Minuten\nTeilnehmer: {teilnehmer}",
                    )
                    await msg.edit(content="", embed=embed, view=None)
                    await deleting.delete()
                else:
                    gewinner = random.randint(1, teilnehmer)

                    async with db.execute(
                        "SELECT user_id FROM giveaway WHERE giveaway_id = ?", (msg.id,)
                    ) as cursor:
                        grow = await cursor.fetchall()
                    for row in grow:
                        teilnehmer2 += 1
                        if gewinner == teilnehmer2:
                            gewinner2 = row[0]
                            embed = discord.Embed(
                                title="Giveaway gewonnen",
                                description=f"Herzlichen Glückwunsch <@{gewinner2}>, du hast das Giveaway gewonnen!",
                                colour=discord.Color.yellow(),
                            )
                            n = datetime.datetime.now()
                            embed.add_field(
                                name="Giveaway Informationen",
                                value=f"Veranstaltet von {interaction.user.mention}\nGestartet um {discord.utils.format_dt(b, 'R')}\nBeendet um {discord.utils.format_dt(n, 'R')}\nDauer des Giveaways: {time / 60} Minuten\nTeilnehmer: {teilnehmer}",
                            )
                            embed.add_field(name="Dauer", value=f"{time / 60} Minuten")
                            await interaction.channel.send(embed=embed)
                            embed2 = discord.Embed(
                                title="Giveaway beendet",
                                description="Siehe unten!",
                                color=discord.Color.nitro_pink(),
                            )
                            await deleting.delete()
                            await msg.edit(
                                content=f"<@{gewinner2}>", embed=embed2, view=None
                            )


class GvwButton(discord.ui.View):
    def __init__(self, msg):
        super().__init__(timeout=None)
        self.msg = msg

    @discord.ui.button(
        label="Am Giveaway teilnehmen",
        style=discord.ButtonStyle.green,
        custom_id="join_giveaway",
    )
    async def button_callback(self, button, interaction):
        async with aiosqlite.connect("giveaway.db") as db:
            async with db.execute(
                "SELECT user_id FROM giveaway WHERE giveaway_id = ? AND user_id = ?",
                (self.msg, interaction.user.id),
            ) as cursor:
                ids = await cursor.fetchall()
                print(ids)
        if ids:
            await interaction.response.send_message(
                "Du nimmst bereits am Giveaway teil. Möchtest du es verlassen?",
                view=LeaveButton(msg=self.msg),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Du nimmst am Giveaway teil!", ephemeral=True
            )
            async with aiosqlite.connect("giveaway.db") as db:
                await db.execute(
                    """
                INSERT INTO giveaway(user_id, giveaway_id)
                VALUES (?,?)
                """,
                    (interaction.user.id, self.msg),
                )
                await db.commit()


class LeaveButton(discord.ui.View):
    def __init__(self, msg):
        super().__init__(timeout=None)
        self.msg = msg

    @discord.ui.button(
        label="Giveaway verlassen", style=discord.ButtonStyle.red, custom_id="leave"
    )
    async def button_callback(self, button, interaction):
        await interaction.response.send_message(
            "Du hast das Giveaway verlassen.", ephemeral=True
        )
        async with aiosqlite.connect("giveaway.db") as db:
            await db.execute(
                """
            DELETE FROM giveaway WHERE user_id = ? and giveaway_id = ?
            """,
                (interaction.user.id, self.msg),
            )
            await db.commit()
