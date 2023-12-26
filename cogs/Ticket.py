import datetime

import discord
import cloudcord
from discord.ext import commands
from discord.commands import slash_command, Option
from discord.ui import Select, View
import json
import asyncio
import time
import chat_exporter
import io


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(EmbedView())
        self.bot.add_view(embedView(self.bot.user))
        self.bot.add_view(TicketSchliesenView(self.bot.user))

    @slash_command()
    @commands.has_permissions(administrator=True)
    async def ticket(self, ctx):
        embed = discord.Embed(
            title="Ticket",
            description="Bevor du unten ein Ticket öffnest, lies kurz die dazugehörigen Beschreibungen.\n"
            "Es werden sich die geeigneten Teamler dann bei dir im Ticket melden.\n"
            "\n"
            "Das Abusen der Tickets führt zum 24h mute.",
            color=discord.Color.blurple(),
        )

        view = EmbedView()

        await ctx.respond(embed=embed, view=view)


def setup(bot):
    bot.add_cog(Ticket(bot))


############################################-------- DROP DOWN 1 MENU --------############################################


class EmbedView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    options = [
        discord.SelectOption(
            label="Support",
            description="Support Ticket | Für: Team",
            value="support",
            emoji="❗",
        ),
        discord.SelectOption(
            label="Team Bewerbung",
            description="Team Bewerbungs Ticket | Für: Team Verwaltung",
            value="bewerbung",
            emoji="👥",
        ),
        discord.SelectOption(
            label="cloudcord/bot",
            description="cloudcord/bot Ticket | Für: ein Problem zu melden",
            value="Problem",
            emoji="🚒",
        ),
    ]

    @discord.ui.select(
        min_values=1,
        max_values=1,
        placeholder="Ticket Auswahl",
        options=options,
        custom_id="dropdown1",
    )
    async def select_callback(self, select, interaction):
        auswahl = select.values[0]

        restricted_role_name = "「❌」 𑁉 SUPPORT SPERRE"
        restricted_role = discord.utils.get(
            interaction.guild.roles, name=restricted_role_name
        )

        if restricted_role in interaction.user.roles:
            await interaction.response.send_message(
                "Du hast nicht die Berechtigung, ein Ticket zu öffnen.", ephemeral=True
            )
            await interaction.message.edit(view=self)
            return

        if auswahl == "support":
            await interaction.response.send_modal(
                SupportModal(interaction.user, title="Support Formular")
            ),
            await interaction.message.edit(view=self)

        if auswahl == "bewerbung":
            await interaction.response.send_modal(
                bewerbenModal(interaction.user, title="Team Bewerbung Formular")
            ),
            await interaction.message.edit(view=self)

        if auswahl == "Problem":
            await interaction.response.send_modal(
                ProblemModal(interaction.user, title="ein Problem zu melden")
            ),
            await interaction.message.edit(view=self)


############################################-------- DROP DOWN 2 MENU --------############################################


class embedView(discord.ui.View):
    def __init__(self, user, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs)
        self.user = user

    options = [
        discord.SelectOption(
            label="User Hinzufügen",
            description="Füge ein User Zum Ticket hinzu",
            value="userhinzufuegen",
            emoji="✨",
        ),
        discord.SelectOption(
            label="User Entfernen",
            description="Entferne ein User vom Ticket",
            value="userentfernen",
            emoji="🌟",
        ),
        discord.SelectOption(
            label="Ticket Schließen",
            description="Schließe das Ticket",
            value="ticketschliesen",
            emoji="🌟",
        ),
    ]

    @discord.ui.select(
        min_values=1,
        max_values=1,
        placeholder="Optionen",
        options=options,
        custom_id="dropdown2",
    )
    async def select_callback2(self, select, interaction):
        auswahl = select.values[0]

        if not interaction.user.guild_permissions.administrator:
            keineberechtigungembed = discord.Embed(
                title="Keine Berechtigungen",
                description="Du hast keine Administratorrechte.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=keineberechtigungembed, ephemeral=True
            )
            await interaction.message.edit(view=self)
            return
        else:
            pass

        if auswahl == "userhinzufuegen":
            await interaction.response.send_modal(
                UserHinzufuegenModal(title="User Hinzufügen")
            )
            await interaction.message.edit(view=self)

        if auswahl == "userentfernen":
            await interaction.response.send_modal(
                UserEntfernenModal(title="User Entfernen")
            )
            await interaction.message.edit(view=self)

        if auswahl == "ticketschliesen":
            await interaction.response.send_modal(
                TicketSchliesenModal(self.user, title="Ticket Schließen")
            )
            await interaction.message.edit(view=self)


###################################-------- USER ZUM TICKET HINZUFÜGEN MODAL --------###################################


class UserHinzufuegenModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="USER ID",
                placeholder="Schreibe die User ID hier rein",
                min_length=18,
                max_length=18,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction):
        user_id = self.children[0].value

        try:
            user_id = int(user_id)
        except ValueError:
            ungueltige_id_embed = discord.Embed(
                title="Ungültige User ID",
                description=f"Bitte gib eine gültige numerische ID ein",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=ungueltige_id_embed, ephemeral=True
            )
            return

        user = interaction.guild.get_member(user_id)

        if not user:
            user_id_embed = discord.Embed(
                title="User nicht Gefunden",
                description=f"Die angegebene User ID wurde nicht gefunden oder gibt es nicht",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=user_id_embed, ephemeral=True)
            return

        text_channel = interaction.channel
        overwrites = text_channel.overwrites

        if user in overwrites:
            user_id_ist_im_ticket = discord.Embed(
                title="User bereits im Ticket",
                description=f"Der User {user.mention} ist bereits im Ticket.",
                color=discord.Color.blue(),
            )
            await interaction.response.send_message(
                embed=user_id_ist_im_ticket, ephemeral=True
            )
            return

        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False,
        )

        overwrites[user] = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            add_reactions=True,
            use_slash_commands=False,
            external_emojis=False,
            use_external_emojis=False,
            mention_everyone=True,
            attach_files=True,
            embed_links=True,
            manage_messages=False,
            send_tts_messages=False,
            create_instant_invite=False,
        )

        await text_channel.edit(overwrites=overwrites)

        embed = discord.Embed(
            title="✅ USER ERFOLGREICH HINZUGEFÜGT ✅",
            description=f"{interaction.user.mention} hat den User {user.mention} zum Ticket Hinzugefügt",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)


###################################-------- USER ZUM TICKET ENTFERNEN MODAL --------###################################


class UserEntfernenModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="USER ID",
                placeholder="Schreibe die User ID hier rein",
                min_length=18,
                max_length=18,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction):
        user_id = self.children[0].value

        try:
            user_id = int(user_id)
        except ValueError:
            ungueltige_id_embed = discord.Embed(
                title="Ungültige User ID",
                description=f"Bitte gib eine gültige numerische ID ein",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=ungueltige_id_embed, ephemeral=True
            )
            return

        user = interaction.guild.get_member(user_id)

        if not user:
            user_id_embed = discord.Embed(
                title="User nicht Gefunden",
                description=f"Die angegebene User ID wurde nicht gefunden oder gibt es nicht",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=user_id_embed, ephemeral=True)
            return

        text_channel = interaction.channel
        overwrites = text_channel.overwrites

        if user in overwrites:
            users_id_ist_im_ticket = discord.Embed(
                title="User ist nicht im ticket",
                description=f"Der User {user.mention} ist nicht im ticket.",
                color=discord.Color.blue(),
            )
            await interaction.response.send_message(
                embed=users_id_ist_im_ticket, ephemeral=True
            )
            return

        overwrites[interaction.guild.default_role] = discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False,
        )

        overwrites[user] = discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False,
            add_reactions=False,
            use_slash_commands=False,
            external_emojis=False,
            use_external_emojis=False,
            mention_everyone=False,
            attach_files=False,
            embed_links=False,
            manage_messages=False,
            send_tts_messages=False,
            create_instant_invite=False,
        )

        await text_channel.edit(overwrites=overwrites)

        embed = discord.Embed(
            title="❌ User erfolgreich entfernt",
            description=f"{interaction.user.mention} hat den User {user.mention} vom Ticket entfernt",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)


########################################-------- TICKET SCHLIEßEN BUTTON --------########################################


class TicketSchliesenView(discord.ui.View):
    def __init__(self, user, *args, **kwargs):
        super().__init__(timeout=None, *args, **kwargs)
        self.user = user

    def disable_buttons_except(self, button):
        for child in self.children:
            if child != button:
                child.disabled = True

    @discord.ui.button(
        label="Akzeptieren & Schließen",
        style=discord.ButtonStyle.green,
        emoji="✅",
        custom_id="button1",
    )
    async def button_callback1(self, button, interaction):
        if self.user.id != interaction.user.id:
            nichtuserembed = discord.Embed(
                title="Du bist nicht der User !",
                description=f"Nur der Ersteller des Tickets ({self.user.mention}) kann das nutzen",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=nichtuserembed, ephemeral=True
            )
            return

        button.disabled = True
        self.disable_buttons_except(button)

        text_channel = interaction.channel
        embed = discord.Embed(
            title="Ticket wird Geschlossen",
            description=f"{interaction.user.mention} hat das Schließen des Tickets Bestätigt.\n"
            f"Das Ticket wird in 5 Sekunden geschlossen",
            color=discord.Color.red(),
        )

        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=embed)

        transcript = await chat_exporter.export(interaction.channel)

        if transcript is None:
            return

        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html",
        )
        log_channel = interaction.client.get_channel(1183612006171934798)

        message = await log_channel.send(file=transcript_file)
        link = await chat_exporter.link(message)

        userembed = discord.Embed(
            title="Dein Ticket wurde geschlossen",
            description=f"Dein Ticket bei ``Cloudcord |  Support `` wurde geschlossen.\n"
            f"```{interaction.channel.name}```\n"
            f"Das Transkript findest du [hier]({link}).",
            color=discord.Color.blue(),
        )

        await interaction.user.send(embed=userembed)

        await asyncio.sleep(5)
        await text_channel.delete()

    @discord.ui.button(
        label="Ablehnen & Offen Lassen",
        style=discord.ButtonStyle.grey,
        emoji="❌",
        custom_id="button2",
    )
    async def button_callback2(self, button, interaction):
        if self.user.id != interaction.user.id:
            nichtuserembed = discord.Embed(
                title="Du bist nicht der User !",
                description=f"Nur der Ersteller des Tickets ({self.user.mention}) kann das nutzen",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(
                embed=nichtuserembed, ephemeral=True
            )
            return

        button.disabled = True
        self.disable_buttons_except(button)

        embed = discord.Embed(
            title="Schließ-Anfrage",
            description=f"{interaction.user.mention} hat die Schließungsanfrage abgelehnt",
            color=discord.Color.red(),
        )

        await interaction.response.edit_message(view=self)
        await interaction.followup.send(embed=embed)


########################################-------- TICKET SCHLIEßEN MODAL --------########################################


class TicketSchliesenModal(discord.ui.Modal):
    def __init__(self, user, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="DER GRUND UM DAS TICKET ZU SCHLIEßEN ",
                placeholder="Grund zum Ticket Schließen",
                min_length=0,
                max_length=100,
            ),
            *args,
            **kwargs,
        )
        self.user = user

    async def callback(self, interaction):
        view = TicketSchliesenView(self.user)
        embed = discord.Embed(
            title="Schließ-Anfrage",
            description=f"{interaction.user.mention} hat das Schließen dieses Tickets angefordert. Grund:\n"
            f"```{self.children[0].value}```",
        )
        await interaction.response.send_message(embed=embed, view=view)


############################################-------- SUPPORT MODAL --------#############################################


class SupportModal(discord.ui.Modal):
    def __init__(self, user, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Wie können wir dir Helfen",
                style=discord.InputTextStyle.long,
                min_length=0,
                max_length=2500,
            ),
            *args,
            **kwargs,
        )
        self.user = user

    async def callback(self, interaction):
        with open("ticketname.json", "r") as f:
            data = json.load(f)
        countersupport = data["countersupport"]
        supportcategory_id = 1167155854202634289  # SUPPORT KATEGORIE
        kategorie = interaction.guild.get_channel(supportcategory_id)

        # Berechtigungen für den erstellten Textkanal festlegen
        overwrites = {
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,  # Nachrichten lesen
                send_messages=True,  # Nachrichten senden
                add_reactions=True,  # Reaktionen hinzufügen
                mention_everyone=False,  # Jeden erwähnen (@everyone und @here)
            )
        }

        # Liste der Support-Rollen
        support_roles = ["Moderator⠀", "Staff Team"]

        for support_role_name in support_roles:
            support_role = discord.utils.get(
                interaction.guild.roles, name=support_role_name
            )
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(
                    read_messages=True,  # Nachrichten lesen
                    send_messages=True,  # Nachrichten senden
                    add_reactions=True,  # Reaktionen hinzufügen
                    mention_everyone=False,  # Jeden erwähnen (@everyone und @here)
                )

        # Berechtigungen für alle anderen Rollen festlegen (Keine Zugriffsrechte)
        for role in interaction.guild.roles:
            if role not in overwrites:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                    add_reactions=False,
                )

                now = datetime.datetime.now()
                timestamp = now.strftime("%A, %d. %B %Y %H:%M")

                ticket_beschreibung = f"Ticket geöffnet am: {timestamp}"  # Das ist die Ticket kanal Beschreibung

        channelsupport = await interaction.guild.create_text_channel(
            f"Support-{countersupport}",
            category=kategorie,
            overwrites=overwrites,
            topic=ticket_beschreibung,
        )

        countersupport += 1
        data["countersupport"] = countersupport
        with open("ticketname.json", "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            title=f"SUPPORT-TICKET",
            description=f"### Willkommen {interaction.user.mention}, \n\n"
            f"**Unser Team wird dir gleich weiterhelfen !**"
            f"\n\n\n"
            f"**Wie können wir dir helfen ?**\n"
            f"- {self.children[0].value}",
            color=discord.Color.green(),
        )

        view = embedView(user=interaction.user)
        embedping = await channelsupport.send(embed=embed, view=view)
        await embedping.pin()

        embed = discord.Embed(
            title="Ticket",
            description=f"Neues Ticket geöffnet {channelsupport.mention}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class bewerbenModal(discord.ui.Modal):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.add_item(
            discord.ui.InputText(
                label="Als was möchtest du dich bewerben ?",
                style=discord.InputTextStyle.long,
                min_length=0,
                max_length=2500,
            )
        )

        self.add_item(
            discord.ui.InputText(
                label="Wie alt bist du ?",
                style=discord.InputTextStyle.long,
                min_length=1,
                max_length=2500,
            )
        )

        self.add_item(
            discord.ui.InputText(
                label="Was sind deine Stärken ?",
                style=discord.InputTextStyle.long,
                min_length=2,
                max_length=2500,
            )
        )

        self.add_item(
            discord.ui.InputText(
                label="Nennen mir 3 nicht so gute Dinge über dich",
                style=discord.InputTextStyle.long,
                min_length=3,
                max_length=2500,
            )
        )

    async def callback(self, interaction):
        with open("ticketname.json", "r") as f:
            data = json.load(f)
        bewerben = data["bewerben"]
        bewerbencategory_id = 1186048508529229884  # bewerbenKATEGORIE
        kategorie = interaction.guild.get_channel(bewerbencategory_id)

        # Berechtigungen für den erstellten Textkanal festlegen
        overwrites = {
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,  # Nachrichten lesen
                send_messages=True,  # Nachrichten senden
                add_reactions=True,  # Reaktionen hinzufügen
                mention_everyone=False,  # Jeden erwähnen (@everyone und @here)
            )
        }

        # Liste der Support-Rollen
        support_roles = ["Moderator⠀⠀", "Staff Team"]

        for support_role_name in support_roles:
            support_role = discord.utils.get(
                interaction.guild.roles, name=support_role_name
            )
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(
                    read_messages=True,  # Nachrichten lesen
                    send_messages=True,  # Nachrichten senden
                    add_reactions=True,  # Reaktionen hinzufügen
                    mention_everyone=False,  # Jeden erwähnen (@everyone und @here)
                )

        # Berechtigungen für alle anderen Rollen festlegen (Keine Zugriffsrechte)
        for role in interaction.guild.roles:
            if role not in overwrites:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                    add_reactions=False,
                )

                now = datetime.datetime.now()
                timestamp = now.strftime("%A, %d. %B %Y %H:%M")

                ticket_beschreibung = f"Ticket geöffnet am: {timestamp}"  # Das ist die Ticket kanal Beschreibung

        channelbewerben = await interaction.guild.create_text_channel(
            f"bewerben-{bewerben}",
            category=kategorie,
            overwrites=overwrites,
            topic=ticket_beschreibung,
        )

        bewerben += 1
        data["bewerben"] = bewerben
        with open("ticketname.json", "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            title=f"Bewerbung - TICKET",
            description=f"Willkommen {interaction.user.mention},\n"
            f"Unser Team wird dir gleich weiterhelfen!\n\n"
            f"Als was möchtest du dich bewerben?\n"
            f"- {self.children[0].value}\n\n"  # Erste Antwort
            f"Wie alt bist du?\n"
            f"- {self.children[1].value}\n\n"  # Zweite Antwort
            f"Was sind deine Stärken?\n"
            f"- {self.children[2].value}\n\n"  # Dritte Antwort
            f"Nenne mir 3 nicht so gute Dinge über dich\n"
            f"- {self.children[3].value}",  # Vierte Antwort
            color=discord.Color.green(),
        )

        view = embedView(user=interaction.user)
        embedping = await channelbewerben.send(embed=embed, view=view)
        await embedping.pin()

        embed = discord.Embed(
            title="Ticket",
            description=f"Neues Ticket geöffnet {channelbewerben.mention}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class ProblemModal(discord.ui.Modal):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.add_item(
            discord.ui.InputText(
                label="wo liegt das Problem ?",
                style=discord.InputTextStyle.long,
                min_length=0,
                max_length=2500,
            )
        )

        self.add_item(
            discord.ui.InputText(
                label="was ist er bug?",
                style=discord.InputTextStyle.long,
                min_length=1,
                max_length=2500,
            )
        )

        self.add_item(
            discord.ui.InputText(
                label="was geht nicht?",
                style=discord.InputTextStyle.long,
                min_length=2,
                max_length=2500,
            )
        )

    async def callback(self, interaction):
        with open("ticketname.json", "r") as f:
            data = json.load(f)
        bugticket = data["bugticket"]
        bugticket_id = 1186046990476378192  # bewerbenKATEGORIE
        kategorie = interaction.guild.get_channel(bugticket_id)

        # Berechtigungen für den erstellten Textkanal festlegen
        overwrites = {
            interaction.user: discord.PermissionOverwrite(
                read_messages=True,  # Nachrichten lesen
                send_messages=True,  # Nachrichten senden
                add_reactions=True,  # Reaktionen hinzufügen
                mention_everyone=False,  # Jeden erwähnen (@everyone und @here)
            )
        }

        # Liste der Support-Rollen
        support_roles = ["Moderator⠀⠀", "Staff Team"]

        for support_role_name in support_roles:
            support_role = discord.utils.get(
                interaction.guild.roles, name=support_role_name
            )
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(
                    read_messages=True,  # Nachrichten lesen
                    send_messages=True,  # Nachrichten senden
                    add_reactions=True,  # Reaktionen hinzufügen
                    mention_everyone=False,  # Jeden erwähnen (@everyone und @here)
                )

        # Berechtigungen für alle anderen Rollen festlegen (Keine Zugriffsrechte)
        for role in interaction.guild.roles:
            if role not in overwrites:
                overwrites[role] = discord.PermissionOverwrite(
                    read_messages=False,
                    send_messages=False,
                    add_reactions=False,
                )

                now = datetime.datetime.now()
                timestamp = now.strftime("%A, %d. %B %Y %H:%M")

                ticket_beschreibung = f"Ticket geöffnet am: {timestamp}"  # Das ist die Ticket kanal Beschreibung

        channelbugticket = await interaction.guild.create_text_channel(
            f"bugticket-{bugticket}",
            category=kategorie,
            overwrites=overwrites,
            topic=ticket_beschreibung,
        )

        bugticket += 1
        data["bugticket"] = bugticket
        with open("ticketname.json", "w") as f:
            json.dump(data, f, indent=4)

        embed = discord.Embed(
            title=f"bug- TICKET",
            description=f"Willkommen {interaction.user.mention},\n"
            f"Unser Team wird dir gleich weiterhelfen!\n\n"
            f"wo liegt das Problem?\n"
            f"- {self.children[0].value}\n\n"  # Erste Antwort
            f"was ist er bug\n"
            f"- {self.children[1].value}\n\n"  # Zweite Antwort
            f"was geht nicht?\n"
            f"- {self.children[2].value}\n\n",  # Dritte Antwort
            color=discord.Color.green(),
        )

        view = embedView(user=interaction.user)
        embedping = await channelbugticket.send(embed=embed, view=view)
        await embedping.pin()

        embed = discord.Embed(
            title="Ticket",
            description=f"Neues Ticket geöffnet {channelbugticket.mention}",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
