import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup, Option
import ezcord

class tempvoiceDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("db/tempvoice.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            server_id INTEGER PRIMARY KEY,
            Category_id INTEGER DEFAULT 0,
            VoiceChannel_id INTEGER DEFAULT 0,
            Channel_id INTEGER DEFAULT 0
            )"""
        )

    async def get_channel(self, guild_id):
        await self.one("SELECT VoiceChannel_id FROM users WHERE server_id = ?",(guild_id))
    
    async def get_txtchannel(self, txt_channel,guild_id):
        async with self.start() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO users (server_id) VALUES (?)", guild_id)
            await cursor.execute(f"UPDATE users SET Channel_id = ? WHERE server_id = ?", txt_channel,guild_id)


    async def get_voice(self, guild_id, voicechannel_id, category_id):
        async with self.start() as cursor:
            # Überprüfe, ob es einen Datensatz für den Server gibt und lege ihn an, falls nicht vorhanden
            await cursor.execute("INSERT OR IGNORE INTO users (server_id) VALUES (?)", (guild_id,))

            # Aktualisiere die VoiceChannel_id und Category_id für den Server
            await cursor.execute("UPDATE users SET VoiceChannel_id = ?, Category_id = ? WHERE server_id = ?", (voicechannel_id, category_id, guild_id))




db = tempvoiceDB()

class Tempvoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channel_id = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TempvoiceView(self.bot))
        tempvoice = SlashCommandGroup("tempvoice")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if self.target_channel_id is None or self.category_id is None:
            return
        if after.channel and after.channel.id == self.target_channel_id:
            if before.channel is None:
                print(f"{member.id} ist dem Ziel-Voice-Chat beigetreten.")
                category = member.guild.get_channel(self.category_id)
                if category and category.type == discord.ChannelType.category:
                    new_channel = await category.create_voice_channel(name=f"{member.name}'s Temp Channel")
                    await member.move_to(new_channel)

    tempvoice = SlashCommandGroup("tempvoice")

    @tempvoice.command(description="Wähle einen Channel")
    async def setup(self, ctx):
        server_name = ctx.guild.name
        embed = discord.Embed(
            title=f'TempVoice Interface von Setup für {server_name}',
            description='Klicke auf die Buttons, um deinen TempChannel zu verwalten.',
            color=discord.Color.blurple()
        )
        await db.get_txtchannel(ctx.channel.id, ctx.guild.id)
        await ctx.channel.send(embed=embed, view=TempvoiceView(self.bot))
        await ctx.respond("Du hast den Kanal ausgewählt", ephemeral=True)

    @tempvoice.command(description="Wähle einen Voicechannel")
    async def voicechannel(
        self, 
        ctx, 
        voicechannel: Option(discord.VoiceChannel, description="Wähle einen Voicechannel", required=True),
        category: Option(discord.CategoryChannel, description="Wähle eine Kategorie", required=True)
    ):
        self.target_channel_id = voicechannel.id
        self.category_id = category.id
        await db.get_voice(ctx.guild.id, voicechannel.id, category.id)
        await ctx.respond("Du hast deinen Voicechannel ausgewählt", ephemeral=True)

def setup(bot):
    bot.add_cog(Tempvoice(bot))

class BanView(discord.ui.View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.channel = channel

    async def select_callback(self, select, interaction):
        banned_users = select.values

        if not banned_users:
            await interaction.response.send_message("Du hast niemanden ausgewählt.")
            return
        for user in banned_users:
            try:
                # Banne den Benutzer aus dem Voice-Channel
                await self.channel.set_permissions(user, connect=False, speak=False)
                await interaction.response.send_message(f"{user.mention} wurde erfolgreich aus dem Voice-Channel gebannt.")
            except discord.Forbidden:
                await interaction.response.send_message(f"Ich habe nicht die Berechtigung, {user.mention} zu bannen.")


class unbanView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.user_select(
        min_values=1,
        max_values=2,
        placeholder="Triff eine Auswahl",
        custom_id="unban"
    )
    async def select_callback(self, select, interaction):
            await interaction.response.send_message(f"Du hast {select.values[0].mention} gewählt.")

class kickView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.user_select(
        min_values=1,
        max_values=2,
        placeholder="Triff eine Auswahl",
        custom_id="kick"
    )
    async def select_callback(self, select, interaction):
            await interaction.response.send_message(f"Du hast {select.values[0].mention} gewählt.")

class OwnerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.user_select(
        min_values=1,
        max_values=2,
        placeholder="Triff eine Auswahl",
        custom_id="Owner"
    )
    async def select_callback(self, select, interaction):
            await interaction.response.send_message(f"Du hast {select.values[0].mention} gewählt.")


class neueslimitModal(discord.ui.Modal):
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


class UmbenennenModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="umbenennen",
                placeholder="Kanal-Name (0= Standard)",
                min_length=1,
                max_length=25,
            ),
            title="Name Des Kanals"
        )

    async def callback(self, interaction):
        umbenennen = self.children[0].value
        try:
            umbenennen_embed = discord.Embed(
                title="Kanal umbenannt",
                description=f"Dein TempChannel heißt nun • 🦕 {umbenennen}",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=umbenennen_embed, ephemeral=True)
        except ValueError:
            Kanalumbenannt_embed = discord.Embed(
                title="Ungültige Kanalumbenennung",
                description=f"Bitte geben Sie einen gültigen •🦕 {umbenennen} ein.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=Kanalumbenannt_embed, ephemeral=True)


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
    async def button_callback1(self, button, interaction):
        embed = discord.Embed()

        if interaction.user.voice and interaction.user.voice.channel:
            if interaction.user.voice.channel.guild.owner_id == interaction.user.id:
                channel = interaction.user.voice.channel

                embed.title = "Ban-Informationen"
                embed.description = f"Du hast erfolgreich {interaction.user.mention} aus dem Voice-Channel gebannt."
                await interaction.response.send_message(embed=embed, view=BanView(channel), ephemeral=True)
            else:
                embed.title = "netter Versuch"
                embed.description = "Du musst der Besitzer des Servers sein, um diese Aktion auszuführen."
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed.title = "oh VC verbinden!"
            embed.description = "Du musst in einem Voice-Channel sein, um diese Aktion auszuführen."
            await interaction.response.send_message(embed=embed, ephemeral=True)


    @discord.ui.button(label="unban", style=discord.ButtonStyle.gray, emoji="🔰", row=1, custom_id="button_unban")
    async def button_callback2(self, select, interaction):
        await interaction.response.send_message(f"{interaction.user.name} kann deinen Kanälen nun wieder beitreten ✨", ephemeral=True, view=unbanView())

    @discord.ui.button(label="Userlimit", style=discord.ButtonStyle.gray, row=1, emoji="👥", custom_id="button_Userlimit")
    async def button_callback3(self, button, interaction):
        await interaction.response.send_modal(neueslimitModal())

    @discord.ui.button(label="umbenennen", style=discord.ButtonStyle.gray, row=1, emoji="📝", custom_id="button_umbenennen")
    async def button_callback4(self, button, interaction):
        await interaction.response.send_modal(UmbenennenModal())

    @discord.ui.button(label="Sperren", style=discord.ButtonStyle.gray, emoji="🔒", row=2, custom_id="button_Sperren")
    async def button_callback5(self, button, interaction):
        await interaction.response.send_message("Du hast deinen TempChannel erfolgreich gesperrt.")

    @discord.ui.button(label="Entsperren", style=discord.ButtonStyle.gray, row=2, emoji="🔓", custom_id="button_Entsperren")
    async def button_callback6(self, button, interaction):
        await interaction.response.send_message("Du hast deinen TempChannel erfolgreich entsperrt. **Jeder darf nun beitreten.**")

    @discord.ui.button(label="kick", style=discord.ButtonStyle.gray, emoji="🔨", row=2, custom_id="button_kick")
    async def button_callback7(self, button, interaction):
        await interaction.response.send_message(f"Du hast dem {interaction.user.name} aus deinem Voicechat gekickt", ephemeral=True, view=kickView())

    @discord.ui.button(label="Neu Owner", style=discord.ButtonStyle.gray, emoji="👑", row=2, custom_id="button_owner")
    async def button_callback8(self, button, interaction):
        await interaction.send_message(f"Du hast dem {interaction.user.name} als neuen Voicechat-Owner gemacht", ephemeral=True, view=OwnerView())