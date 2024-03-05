import discord
from discord.commands import SlashCommandGroup
import ezcord
from datetime import datetime
import chat_exporter
import asyncio
import io




class ticketDB(ezcord.DBHandler):
    def __init__(self):
        """
        """
        super().__init__("db/ticket.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS ticket(
            server_id INTEGER PRIMARY KEY,
            category_id INTEGER DEFAULT 0,
            teamrole_id INTEGER DEFAULT 0,
            logs_Channel_id INTEGER DEFAULT 0
            )"""
        )



    async def set_category(self, server_id, category_id):
        await self.execute(
            "INSERT INTO ticket (server_id, category_id) VALUES (?, ?) ON CONFLICT(server_id) DO UPDATE SET category_id = ?",
            (server_id, category_id, category_id )
        )

    async def get_category(self, server_id):
        return await self.one("SELECT category_id FROM ticket WHERE server_id = ?", (server_id,))
    


    async def set_teamrole(self, server_id, teamrole_id):
        await self.execute(
            "INSERT INTO ticket (server_id, teamrole_id) VALUES (?, ?) ON CONFLICT(server_id) DO UPDATE SET teamrole_id = ?",
            (server_id, teamrole_id, teamrole_id)
        )

    async def get_teamrole(self, server_id):
        return await self.one("SELECT teamrole_id FROM ticket WHERE server_id = ?", (server_id,))
    




    async def set_logs_Channel(self, server_id,logs_Channel_id):
        await self.execute(
            "INSERT INTO ticket (server_id, logs_Channel_id) VALUES (?, ?) ON CONFLICT(server_id) DO UPDATE SET logs_Channel_id = ?",
            (server_id, logs_Channel_id, logs_Channel_id )
        )

    async def get_logs_Channel(self, server_id):
        return await self.one("SELECT logs_Channel_id FROM ticket WHERE server_id = ?", (server_id,))






db = ticketDB()

options = [
    discord.SelectOption(label="Support", description="If you need support, please open a ticket", emoji="🎫"),
    discord.SelectOption(label="Report user", description="report a user", emoji="👥"),
    discord.SelectOption(label="Apply for team", description="Apply for your team ", emoji="💼"),
]

class Ticketv2(ezcord.Cog, emoji="🎫"):


    @ezcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CreateTicket())
        self.bot.add_view(Ticket())
        self.bot.add_view(ticketSettings())






    ticket = SlashCommandGroup("ticket", default_member_permissions=discord.Permissions(administrator=True))




    @ticket.command(name="setup",description="Create a ticket")
    @discord.guild_only()
    async def setup_commmand(self, ctx, logs: discord.TextChannel,  category: discord.CategoryChannel, role: discord.Role):
        server_id = ctx.guild.id
        category_id = category.id
        teamrole_id = role.id
        logs_channel_id = logs.id
        await db.set_logs_Channel(server_id, logs_channel_id)
        await db.set_category(server_id, category_id)
        await db.set_teamrole(server_id, teamrole_id)
        embed = discord.Embed(
            title="Create a ticket",
            description="**If you need support, click `📨 Create ticket` button below and create a ticket!**",
            color=discord.Color.dark_green()
        )
        embed.timestamp = datetime.utcnow()
        await ctx.channel.send(embed=embed, view=CreateTicket())
        await ctx.respond("It was sent successfully", ephemeral=True)


    @ticket.command(name="settings", description="set your ticket system here")
    async def settingscommand(self, ctx):
        emmed = discord.Embed(
            title="**Ticket settings**",
            description="make your ticket system better!",
            color=discord.Color.blue()
        )
        await ctx.respond(embed=emmed, view=ticketSettings(), ephemeral=True)







def setup(bot):
    bot.add_cog(Ticketv2(bot))


class ticketSettings(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Who can close the ticket?", style=discord.ButtonStyle.blurple, emoji="<:__:1214322496887853066>", custom_id="who_button")
    async def handle_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Please use the dropdown menu to select an option.", view=SettingsClose(), ephemeral=True)

options = [
    discord.SelectOption(label="Only Moderators", emoji="<:mod:1214322015981273108>"),
    discord.SelectOption(label="All Users", emoji="<:user:1214377500621414452>")
]

class SettingsClose(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="settingsclose",
        min_values=1,
        max_values=1,
        placeholder="Determine who can close the ticket",
        options=options,
    )
    async def handle_dropdown(self, select, interaction):
        selected_option = interaction.data["values"][0]
        embed = discord.Embed(
            title="🎟 Who can close the ticket",
            description=f"Selected option: `{selected_option}`"
        )
        await interaction.respond(embed=embed, view=weiterbutton(), ephemeral=True)



class weiterbutton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="further", style=discord.ButtonStyle.green, emoji="▶", custom_id="weider_button")
    async def weiter_back(self, button, interaction):
        embed = discord.Embed(
            title="do you want to continue?",
            description="If yes, you can continue again.",
            color=discord.Color.embed_background()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True, view=ticketname())

    @discord.ui.button(label="no thanks, I'm done", style=discord.ButtonStyle.red, emoji="🔒")
    async def no_back(self, button, interaction):
        embed = discord.Embed(
            title="No thanks",
            description=f"no thanks, I'm done",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
class ticketname(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) 

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, emoji="📨", custom_id="create_ticket")
    async def button_callback1(self, button, interaction):
        server_id = interaction.guild.id

        embed = discord.Embed(
            title="Create Ticket",
            description="Choose your ticket",
            color=discord.Color.blurple()
        )
        await interaction.respond(embed=embed, view=CreateTicketSelect(), ephemeral=True)



class CreateTicketSelect(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="bro_ich_weiss_nicht",
        min_values=1,
        max_values=2,
        placeholder="Make a selection of your ticket",
        options=options,
    )
    async def ticket_select_callback(self, select, interaction):
        category_id = await db.get_category(interaction.guild.id)
        teamrole_id = await db.get_teamrole(interaction.guild.id)

        if category_id:
            category = discord.utils.get(interaction.guild.categories, id=category_id)
            
            if category:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    interaction.user: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True),
                    interaction.guild.me: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True),
                }
                team_role = interaction.guild.get_role(teamrole_id)
                if team_role:
                    topic = f"Ticket for {interaction.user.name}. Contact {team_role.mention} for assistance."
                else:
                    topic = f"Ticket for {interaction.user.name}. Contact staff for assistance."

                channel = await category.create_text_channel(name=f"{interaction.user.display_name}", overwrites=overwrites, topic=topic)

                msg = await channel.send(f"{team_role.mention if team_role else '@staff'} {interaction.user.mention} has opened a ticket.")
                embed = discord.Embed(
                title="🎉 Welcome to Customer Support! 🎉",
                description="Welcome to our customer support! We sincerely appreciate you taking the time to reach out to us. Your concern is important to us, and we want to ensure that you receive the best possible assistance.\n\nYour ticket has been successfully created, and our dedicated team is standing by to assist you with any questions, issues, or concerns you may have. We understand that you may be awaiting a prompt resolution, and we are committed to responding to you as quickly as possible.\n\nPlease understand that processing your ticket may take some time as we aim to ensure that we provide you with the highest quality support. Your satisfaction is our priority, and we will spare no effort to ensure that your needs are met.\n\nWhile you wait for a response, please rest assured that we have received your message and are working to reply to you as soon as possible. Your patience is greatly appreciated.\n\nFeel free to contact us if you need further assistance or have any questions. Our team is available around the clock and is ready to assist you. We are here to help you and ensure that you have a positive experience.\n\nThank you for trusting our support team and for the opportunity to serve you!",
                color=discord.Color.green()
            )


                await channel.send(embed=embed , view=Ticket())
                await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}", ephemeral=True)
                return

        await interaction.response.send_message("The category ID is not set in the database or the specified category doesn't exist.", ephemeral=True)

options = [
    discord.SelectOption(label="Add User", description="Add User to ticket", emoji="👥"),
    discord.SelectOption(label="Remove User", description="Remove a user from ticket", emoji="<:redcross:758380151238033419>"),
 
]

class Ticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.button_pressed = False

    @discord.ui.button(label="Ticket accepted", style=discord.ButtonStyle.green, emoji="🗂️", row=1,custom_id="accepted_button")
    async def assume_ticket(self, button, interaction):
        team_role_id = await db.get_teamrole(interaction.guild.id)
        if team_role_id is None:
            await interaction.response.send_message(
                "The team role has not been configured. Please contact the administrator.", ephemeral=True)
            return

        team_role = interaction.guild.get_role(team_role_id)
        if team_role is None:
            await interaction.response.send_message(
                "The configured team role was not found. Please contact the administrator.", ephemeral=True)
            return

        if team_role not in interaction.user.roles:
            await interaction.response.send_message("You are not authorized to accept this ticket.", ephemeral=True)
            return

        if self.button_pressed:
            await interaction.response.send_message("You have already accepted the ticket.", ephemeral=True)
            return

        await interaction.response.defer()
        member = interaction.user
        embed = discord.Embed(
            title="Ticket accepted",
            description=f"{member.mention} will now attend to your request!",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)

        self.button_pressed = True

    @discord.ui.button(label="Close", style=discord.ButtonStyle.blurple, emoji="🔐", row=1, custom_id="close_ticket")
    async def close_ticket(self, button, interaction):
        team_role_id = await db.get_teamrole(interaction.guild.id)
        if team_role_id in [role.id for role in interaction.user.roles]:
            server_id = interaction.guild.id

            embed = discord.Embed(
                title="Close Ticket",
                description="Deleting Ticket in less than `5 Seconds`... ⏳\n\n"
                            "_If not, you can do it manually!_",
                color=discord.Color.dark_red()
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
            log_channel_id = await db.get_logs_Channel(server_id)
            log_channel = interaction.client.get_channel(log_channel_id)

            message = await log_channel.send(file=transcript_file)
            link = await chat_exporter.link(message)

            topic = interaction.channel.topic
            ticket_owner_name = topic.split("Ticket for ")[1].split(".")[0]

            ticket_owner = discord.utils.get(interaction.guild.members, name=ticket_owner_name)

            if ticket_owner:
                userembed = discord.Embed(
                    title="Your ticket has been closed",
                    description=f"Your ticket has been closed.\n"
                                f"```{interaction.channel.name}```\n"
                                f"You can find the transcript [here]({link}).",
                    color=discord.Color.blue(),
                )
                await ticket_owner.send(embed=userembed)

            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            embed = discord.Embed(
                title="Unauthorized",
                description=f"You do not have the necessary role  close tickets.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

    @discord.ui.select(
    custom_id="ticket_actions",
    min_values=1,
    max_values=2,
    placeholder="Choose an action",
    options=options,
    )
    async def callback(self, select, interaction):
        server_id = interaction.guild.id
        teamrole_id = await db.get_teamrole(server_id)
        
        user_roles = [role.id for role in interaction.user.roles]
        

        if teamrole_id in user_roles:
            selected_options = interaction.data['values']
            channel = interaction.channel
            await interaction.message.edit(view=self)
            if "Add User" in selected_options:
                await interaction.response.send_modal(UserModal())
            elif "Remove User" in selected_options:
                await interaction.response.send_modal(removeuser())








class UserModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="User",
                placeholder="User ID",
                style=discord.InputTextStyle.short,
                custom_id="add_user",
            ),
            title="Add User to Ticket"
        )

    async def callback(self, interaction):
        user = interaction.guild.get_member(int(self.children[0].value))
        if user is None:
            return await interaction.response.send_message("Invalid user ID, make sure the user is in this guild!", ephemeral=True)
        overwrite = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        await interaction.channel.set_permissions(user, overwrite=overwrite)
        await interaction.response.send_message(content=f"{user.mention} has been added to this ticket!", ephemeral=True)

class removeuser(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Remove User",
                placeholder="User ID",
                style=discord.InputTextStyle.short,
                custom_id="remove_user",
            ),
            title=" Remove user to Ticket"
        )

    async def callback(self, interaction):
        user = interaction.guild.get_member(int(self.children[0].value))
        if user is None:
            return await interaction.response.send_message("Invalid user ID, make sure the user is in this guild!", ephemeral=True)
        overwrite = discord.PermissionOverwrite(view_channel=False, send_messages=False, read_message_history=False)
        await interaction.channel.set_permissions(user, overwrite=overwrite)
        await interaction.response.send_message(content=f"{user.mention} has been Remove to this ticket!", ephemeral=True)




