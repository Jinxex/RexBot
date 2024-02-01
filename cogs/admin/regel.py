import datetime
import ezcord
from discord.commands import option, slash_command
import discord



class Regelwerk(ezcord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="regelwerk")
    @discord.default_permissions(administrator=True)
    @option("channel", description="Gebe den Kanal wo das Regelwerk reingesendet werden soll")
    async def regelwerk(self, ctx: ezcord.EzContext, channel: discord.TextChannel):
        embed = discord.Embed(
            title=f"🏠**__Offizielles Discord Regelwerk von Flexii Development**",
            description="`💬` **__Text-Regeln__**\n"
            "`💬` **›** Kein Spam: `2-stündigen Timeout.`\n"
            "`☠️` **›** Keine Beschimpfung: `5-stündigen Timeout.`\n"
            "`⚔️` **›** Ausnutzen von Rechten: `Team Kick und 12-stündiger Timeout.`\n"
            "`🧩` **›** Werbung: `24-stündigen Timeout.`\n"
            "`🎭` **›** Diskriminierung: `12-stündigen Timeout.`\n"
            "`⚙️` **›** Kopieren des Servers (ohne Absprache): `Ban und Meldung an den Server.`\n"
            "`📝` **›** Kein Betteln um Rollen: `Team Verweis oder 4-stündiger Timeout.`\n\n"
            "`🔊` **__Voice-Regel__**\n"
            "`🎶` **›** Spammen vom Soundboard: `5-stündiger Timeout.`\n"
            "`🎤` **›** Häufiges Voice Channel wechseln: `12-stündiger Timeout.`\n"
            "`🔇` **›** Kein Stimmverzehrer: `24-stündiger Timeout.`\n"
            "`🎧` **›** Keine übertönten Töne: `6-stündiger Timeout.`\n"
            "`🎬` **›** Unerlaubtes Aufnehmen: `Meldung bei Discord und 48-stündiger Timeout.`\n"
            "`🎥` **›** Livestream Spamming: `4-stündiger Timeout.`\n\n"
            "`🌀` **›** **Mit dem Beitreten des Servers akzeptierst du automatisch das Regelwerk und"
            " verpflichtest dich, dich an diese Regeln zu halten."
            " Bei Verstößen gegen diese Regeln wirst du entsprechend bestraft.**\n\n"
            "`🗓️` **›** **Änderungen am Regelwerk:**"
            " Es dürfen **jederzeit Änderungen** am Regelwerk vorgenommen werden,"
            " auch ohne vorherige Benachrichtigung.\n \n"
            f"`⚖️` **›** Das Regelwerk wurde zuletzt **am {datetime.datetime.now().strftime('%d.%m.%Y')}**"
            f" aktualisiert.\n\n"
            "`🆘` **›** Wenn du einen Regelbrecher findest kannst du"
            " diesen in einem <#1202310679256637440> melden.",
            color=3716863,
        )
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            return await ctx.error(
                "Ich hab leider keine Rechte das Embed in diesen Kanal zu senden"
            )
        await ctx.success(f"Ich habe das Embed erfolgreich in {channel.mention} geschickt")


def setup(bot):
    bot.add_cog(Regelwerk(bot))
