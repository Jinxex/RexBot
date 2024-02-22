import discord
from discord.ext import commands
from discord.commands import slash_command
import ezcord
from datetime import datetime
import asyncio

CATEGORY = "⚡ Support"


options = [
        discord.SelectOption(label="suppert", description="suppert Beschreibung", emoji="🎫"),
        discord.SelectOption(label="", description="Java Beschreibung", emoji="💻"),
        discord.SelectOption(label="Javascript", description="Javascript Beschreibung", emoji="🚩", value="JS")
    ]


class Ticketv2(ezcord.Cog, emoji="🎫"):



    @ezcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(CreateTicket())
        self.bot.add_view(CloseTicket())





    @slash_command(description="Create a ticket")
    async def ticketv2(self, ctx):
        embed = discord.Embed(
            title="Create a ticket",
            description="**If you need support, click `📩 Create ticket` button below and create a ticket!**",
            color=discord.Color.dark_green()
        )
        embed.timestamp = datetime.utcnow()
        await ctx.channel.send(embed=embed, view=CreateTicket())
        await ctx.respond("It was sent successfully", ephemeral=True)

def setup(bot):
    bot.add_cog(Ticketv2(bot))

class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)



    @discord.ui.select(
        min_values=1,
        max_values=2,
        placeholder="Triff eine Auswahl",
        options=options,
    )


    @discord.ui.button(label="Create ticket", style=discord.ButtonStyle.blurple, emoji="📩", custom_id="Create_ticket")
    async def create_ticket(self, button, interaction):
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True, read_message_history=True, send_messages=True),
        }
        category = discord.utils.get(interaction.guild.categories, name=CATEGORY)
        if category:
            channel = await category.create_text_channel(name=f"{interaction.user.display_name}", overwrites=overwrites, topic=interaction.user.name)
            embed = discord.Embed(
                title="Ticket Created",
                description="Support will be with you shortly.",
                color=discord.Color.green()
            )
            await channel.send(embed=embed, view=CloseTicket())
            await interaction.response.send_message(f"I've opened a ticket for you at {channel.mention}", ephemeral=True)
        else:
            await interaction.response.send_message("I couldn't find the specified category.", ephemeral=True)


#________________________________________________________________________________________________________________#

class CloseTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.blurple, emoji="🔐", custom_id="close_ticket")
    async def close_ticket(self, button, interaction):
        topic = interaction.channel.topic
        if interaction.user.name == topic or interaction.user == interaction.guild.owner:
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
                description="You are not the server owner or the ticket user.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="user", style=discord.ButtonStyle.gray, emoji="👥", row=1, custom_id="user" )
    async def user_ticket(self, button, interaction):
        await interaction.response.send_modal(UserModal())


    @discord.ui.button(label="Role", style=discord.ButtonStyle.gray, emoji="📌", row=2, custom_id="role_add" )
    async def role_ticket( self, button, interaction):
        await interaction.response.send_modal(RoleModal())


    @discord.ui.button(label="remove a user", style= discord.ButtonStyle.gray, emoji="🌀", row=3, custom_id="remove_user")
    async def romove_user(self, button, interaction):
        await interaction.response.send_modal(removeuser())


#___________________________________________________________________________________________________#

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

#________________________________________________________________________________________________________________#

class RoleModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Role",
                placeholder="Role ID",
                style=discord.InputTextStyle.short,
                custom_id="add_role",
            ),
            title="Add Role to Ticket"
        )

    async def callback(self, interaction):
        role = interaction.guild.get_role(int(self.children[0].value))
        if role is None:
            return await interaction.response.send_message("Invalid role ID, make sure the role is in this guild!", ephemeral=True)
        overwrite = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        await interaction.channel.set_permissions(role, overwrite=overwrite)
        await interaction.response.send_message(content=f"{role.mention} has been added to this ticket!", ephemeral=True)

#________________________________________________________________________________________________________________#
        



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





#___________________________________________________________________________________________________________________________________#


