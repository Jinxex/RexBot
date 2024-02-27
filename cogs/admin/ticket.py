import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.ext import commands
import ezcord
from datetime import datetime
import asyncio

class ticketDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("db/ticket.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS ticket(
            server_id INTEGER PRIMARY KEY,
            category_id INTEGER DEFAULT 0,
            teamrole_id INTEGER DEFAULT 0
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
        #self.bot.add_view(frageticket())


    @slash_command(description="Create a ticket")
    @discord.guild_only()
    async def ticket(self, ctx, category: discord.CategoryChannel, role: discord.Role):
        if ctx.author.guild_permissions.administrator:
            server_id = ctx.guild.id
            category_id = category.id
            teamrole_id = role.id
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
        else:
            await ctx.respond("Error: You don't have permissions to use this command.", ephemeral=True)

def setup(bot):
    bot.add_cog(Ticketv2(bot))

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
        custom_id="bro ich weiss nicht",
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
                    title="Ticket Created",
                    description="Support will be with you shortly.",
                    color=discord.Color.green()
                )

                await channel.send(embed=embed , view=Ticket())
                await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}", ephemeral=True)
                return

        await interaction.response.send_message("The category ID is not set in the database or the specified category doesn't exist.", ephemeral=True)

options = [
    discord.SelectOption(label="Add User", description="Add User to ticket", emoji="👥"),
    discord.SelectOption(label="Remove User", description="Remove a user from ticket", emoji="<:redcross:758380151238033419>"),
    discord.SelectOption(label="Do you still have questions?", emoji="❓"),
]

class Ticket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.button_pressed = False

    @discord.ui.button(label="Ticket accepted", style=discord.ButtonStyle.green, emoji="🗂️", row=1, custom_id="accepted_button")
    async def assume_ticket(self, button, interaction):
        team_role_id = await db.get_teamrole(interaction.guild.id)
        if team_role_id is None:  
            await interaction.response.send_message("Die Teamrolle wurde nicht konfiguriert. Bitte kontaktiere den Administrator.", ephemeral=True)
            return

        team_role = interaction.guild.get_role(team_role_id)
        if team_role is None:
            await interaction.response.send_message("Die konfigurierte Teamrolle wurde nicht gefunden. Bitte kontaktiere den Administrator.", ephemeral=True)
            return

        if team_role not in interaction.user.roles:
            await interaction.response.send_message("Du bist nicht autorisiert, dieses Ticket anzunehmen.", ephemeral=True)
            return

        if self.button_pressed:
            await interaction.response.send_message("Du hast das Ticket bereits angenommen.", ephemeral=True)
            return

        await interaction.response.defer()
        team_role_id = await db.get_teamrole(interaction.guild.id)
        if team_role_id in [role.id for role in interaction.user.roles]:
            server_id = interaction.guild.id
        member = interaction.user
        embed = discord.Embed(
            title="Ticket angenommen",
            description=f"{member.mention} wird sich nun um deine Anfrage kümmern!",
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
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            embed = discord.Embed(
                title="No Permission ❌",
                description="You do not have permission to close this ticket.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)




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
            elif "Do you still have questions?" in selected_options:
                embed = discord.Embed(
                    title="It's coming soon",
                    description="This doesn't work yet due to bugs, it's coming soon",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                #ticket_opener = channel.topic
                #msg = await channel.send(f"{interaction.user.mention} has opened a ticket.")
                #embed = discord.Embed(
                    #title="Additional Questions",
                    #description=f"Hey {ticket_opener}, if you have no further questions or don't click anything, the ticket will automatically close in 12 hours.",
                    #color=discord.Color.gold()
                #)
                #embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                #await interaction.response.send_message(content=msg.content, embed=embed, view=frageticket())
        #else:
            #error_embed = discord.Embed(
                #title="Access Denied",
                #description="You do not have the required role to perform this action.",
                #color=discord.Color.red()
            #)
            #await interaction.response.send_message(embed=error_embed, ephemeral=True)


#class frageticket(discord.ui.View):
    #def __init__(self, user_in_db=False):
        #super().__init__(timeout=None)
        #self.user_in_db = user_in_db

    #async def check_user_in_db(self, interaction):
        #server_id = interaction.guild.id


    #@discord.ui.button(label="Yes, I still have questions", style=discord.ButtonStyle.primary, row=1, emoji="🎟️", custom_id="frage_ticket")
    #async def ask_back(self, button, interaction):


            #ticket_opener = interaction.channel.topic
            #embed = discord.Embed(
                #title="Ask questions",
                #description=f"All clear {ticket_opener}, you can now ask your questions.",
                #color=discord.Color.green()
           # )
            #await interaction.response.send_message(embed=embed)

    #@discord.ui.button(label="No, all done", style=discord.ButtonStyle.green, row=1, emoji="✅", custom_id="no_ticket")
    #async def no_back(self, button, interaction):
       # server_id = interaction.guild.id
        #await asyncio.sleep(1)
       # await interaction.channel.delete()





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