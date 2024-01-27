import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import ezcord

class tempvoiceDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("database/tempvoice.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            server_id INTEGER PRIMARY KEY,
            VoiceChannel_id INTEGER DEFAULT 0,
            Channel_id INTEGER DEFAULT 0
            )"""
        )

    async def get_channel(self, guild_id):
        return await self.execute(f"SELECT VoiceChannel_id FROM users WHERE server_id = {guild_id}")
    
    async def get_txtchannel(self, txt_channel,guild_id):
        async with self.start() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO users (server_id) VALUES (?)", guild_id)
            await cursor.execute(f"UPDATE users SET Channel_id = ? WHERE server_id = ?", txt_channel,guild_id)


    async def get_voice(self, guild_id,voicechannel_id):
        async with self.start() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO users (server_id) VALUES (?)", guild_id)
            await cursor.execute("UPDATE users SET VoiceChannel_id = ? WHERE server_id = ?", voicechannel_id, guild_id)
db = tempvoiceDB()

class Tempvoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TempvoiceView(self.bot))

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            voicechannel_id = await db.get_channel(member.guild.id)
            if after.channel is not None and after.channel.id == voicechannel_id:
                print(f"{member.name} ist dem temporären Sprachkanal beigetreten.")

    tempvoice = SlashCommandGroup("tempvoice")

    @tempvoice.command(description="Wähle einen Channel")
    async def setup(self, ctx):
        await db.get_txtchannel(ctx.channel.id,ctx.guild.id)
        await ctx.channel.send(view=TempvoiceView(self.bot))
        await ctx.respond("Du hast den Kanal ausgewählt", ephemeral=True)

    @tempvoice.command(description="Wähle einen Voicechannel")
    async def voicechannel(self, ctx, voicechannel: Option(discord.VoiceChannel, description="Wähle einen Voicechannel", required=True)):
        await db.get_voice(ctx.guild.id, voicechannel.id)
        await ctx.respond("Du hast deinen Voicechannel ausgewählt", ephemeral=True)

def setup(bot):
    bot.add_cog(Tempvoice(bot))

class TempvoiceModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="neues limit",
                placeholder="Zahl zwischen 0 und 99(0=Kein Limit)",
                min_length=1,
                max_length=99,
            ),
            title="TempChannel bearbeiten"
        )

    async def callback(self, interaction):
        user_limit = self.children[0].value
        try:
            user_limit = int(user_limit)
            userlimit_embed1 = discord.Embed(
                title="User limit geändert",
                description=f"du hast das user Limit auf {user_limit}  gemacht!",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=userlimit_embed1, ephemeral=True)
        except ValueError:
            userlimit_embed = discord.Embed(
                title="Ungültige User limit",
                description=f"Bitte gib eine gültige USER limit ein",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=userlimit_embed, ephemeral=True)




class TempvoiceView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def is_user_in_tempvoice(self, user, guild_id):
        voice_channel_id = await db.get_channel(guild_id)
        if voice_channel_id is not None:
            voice_channel = self.bot.get_channel(voice_channel_id)
            member = voice_channel.guild.get_member(user.id)
            return member is not None and member.voice is not None and member.voice.channel == voice_channel
        return False

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.gray, emoji="⛔", row=1, custom_id="button_ban")
    async def button_callback1(self, button,  interaction):
        await interaction.response.send_message(f"Du hast erfolgreich {interaction.user.name} aus deinen Kanälen gebannt.", ephemeral=True)

    @discord.ui.button(label="unban", style=discord.ButtonStyle.gray, emoji="🔰", row=1, custom_id="button_unban")
    async def button_callback2(self, button, interaction):
        await interaction.response.send_message(f"{interaction.user.name} kann deinen Kanälen nun wieder beitreten ✨", ephemeral=True)

    @discord.ui.button(label="Userlimit", style=discord.ButtonStyle.gray, row=1, emoji="👥", custom_id="button_Userlimit")
    async def button_callback3(self, button, interaction):
        await interaction.response.send_modal(TempvoiceModal())

    @discord.ui.button(label="umbenennen", style=discord.ButtonStyle.gray, row=1, emoji="📝", custom_id="button_umbenennen")
    async def button_callback4(self, button, interaction):
        await interaction.response.send_message("Du hast deinen Voicechat auf  umbenannt")

    @discord.ui.button(label="Sperren", style=discord.ButtonStyle.gray, emoji="🔒", row=2, custom_id="button_Sperren")
    async def button_callback5(self, button, interaction):
        await interaction.response.send_message("Du hast deinen TempChannel erfolgreich gesperrt.")

    @discord.ui.button(label="Entsperren", style=discord.ButtonStyle.gray, row=2, emoji="🔓", custom_id="button_Entsperren")
    async def button_callback6(self, button, interaction):
        await interaction.response.send_message("Du hast deinen TempChannel erfolgreich entsperrt. **Jeder darf nun beitreten.**")

    @discord.ui.button(label="kick", style=discord.ButtonStyle.gray, emoji="🔨", row=2, custom_id="button_kick")
    async def button_callback7(self, button, interaction):
        await interaction.response.send_message(f"Du hast dem {interaction.user.name} aus deinem Voicechat gekickt")

    @discord.ui.button(label="Neu Owner", style=discord.ButtonStyle.gray, emoji="👑", row=2, custom_id="button_owner")
    async def button_callback8(self, button, interaction):
        await interaction.send_message(f"Du hast dem {interaction.user.name} als neuen Voicechat-Owner gemacht")