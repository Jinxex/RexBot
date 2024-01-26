import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import littxlecord

class tempvoiceDB(littxlecord.DBHandler):
    def __init__(self):
        super().__init__("database/tempvoice.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            server_id BIGINT PRIMARY KEY,
            VoiceChannel_id INTEGER DEFAULT 0,
            Channel_id INTEGER DEFAULT 0
            )"""
        )

db = tempvoiceDB()

class Tempvoice(littxlecord.Cog):

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TempvoiceView())

    tempvoice = SlashCommandGroup("tempvoice")

    @tempvoice.command(description="Wähle einen Channel")
    async def setup(self, ctx):
        await ctx.channel.send(view=TempvoiceView())
        await ctx.respond("du hast dem channel aus gewählt", ephemeral=True)

    @tempvoice.command(description="Wähle einen Voicechannel")
    async def voicechannel(self, ctx, voicechannel: Option(discord.VoiceChannel, description="Wähle einen Voicechannel", required=True)):
        await ctx.respond("Du hast deinen Voicechannel ausgewählt",ephemeral=True)


def setup(bot):
    bot.add_cog(Tempvoice(bot))


class embedview(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label="weiter", style=discord.ButtonStyle.green, row=1, emoji="➡", custom_id="button_wieter")
    async def button_callback(self, button, interaction):
        await interaction.send_message("test")



class TempvoiceModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Limit",
                placeholder="Zahl zwischen 0 und 99(0=Kein Limit)"
            ),
        )
        
    async def callback(self, interaction):
        embed = discord.Embed(
            title=self.children[0].value,
            description=self.children[1].value,
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)


class TempvoiceView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.gray, emoji="⛔", row=1, custom_id="button_ban")
    async def button_callback1(self, button, interaction):
        await interaction.response.send_message(f"Du hast dem {interaction.user.name} aus deinem Voicechat gebannt", ephemeral=True)

    @discord.ui.button(label="unban", style=discord.ButtonStyle.gray, emoji="🔰", row=1, custom_id="button_unban")
    async def button_callback2(self, button, interaction):
        await interaction.response.send_message(f"Du hast dem {interaction.user.name} aus deinem Voicechat unbanned")

    @discord.ui.button(label="Userlimit", style=discord.ButtonStyle.gray, row=1, emoji="👥", custom_id="button_Userlimit")
    async def button_callback3(self, button, interaction):
        await interaction.response.send_modal(TempvoiceModal(title="Hast du deinen Voicechat auf Userlimit gesetzt"))

    @discord.ui.button(label="umbenennen", style=discord.ButtonStyle.gray, row=1, emoji="📝", custom_id="button_umbenennen")
    async def button_callback4(self, button, interaction):
        await interaction.response.send_message("Du hast deinen Voicechat auf  umbenannt")

    @discord.ui.button(label="Sperren", style=discord.ButtonStyle.gray, emoji="🔒", row=2, custom_id="button_Sperren")
    async def button_callback5(self, button, interaction):
        await interaction.response.send_message("Jetzt kann keiner mehr in den Voicechat rein")

    @discord.ui.button(label="Entsperren", style=discord.ButtonStyle.gray, row=2, emoji="🔓", custom_id="button_Entsperren")
    async def button_callback6(self, button, interaction):
        await interaction.response.send_message("Jetzt kann jeder wieder in den Voicechat rein")

    @discord.ui.button(label="kick", style=discord.ButtonStyle.gray, emoji="🔨", row=2, custom_id="button_kick")
    async def button_callback7(self, button, interaction):
        await interaction.response.send_message(f"Du hast dem {interaction.user.name} aus deinem Voicechat gekickt")

    @discord.ui.button(label="Neu Owner", style=discord.ButtonStyle.gray, emoji="👑", row=2, custom_id="button_owner")
    async def button_callback8(self, button, interaction):
        await interaction.send_message(f" du hast dem {interaction.user.name} als neu  Voicechat  Owner gemacht")