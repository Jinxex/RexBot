import discord
import ezcord
from discord.commands import slash_command

class ticketDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("db/ticket.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            server_id INTEGER PRIMARY KEY,
            team_id INTEGER DEFAULT 0,
            logs_id INTEGER DEFAULT 0,
            close_id INTEGER DEFAULT 0
            )"""
        )

db = ticketDB()

options = [
    discord.SelectOption(label="ticket", emoji="🎫"),
    discord.SelectOption(label="user melden", emoji="👥"),
    discord.SelectOption(label="...", emoji="📌")
]

class Ticketv2(ezcord.Cog, emoji="🎫"):

    def __init__(self, bot):
        self.bot = bot

    @ezcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView())

    @slash_command(description="Setup your ticket")
    async def ticket_setup(self, ctx, role: discord.Role, category: discord.CategoryChannel, logs: discord.TextChannel):
        embed = discord.Embed(
            title="Ticket System",
            description="You can contact the server team here.",
            color=discord.Color.blurple()
        )
        await ctx.respond(embed=embed, view=TicketView())

def setup(bot):
    bot.add_cog(Ticketv2(bot))

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="ticket_select",
        min_values=1,
        max_values=1,
        placeholder="📝• Triff eine Auswahl",
        options=options,
    )
    async def callback(self, select, interaction):
        if select.values[0] == "user melden":
            await self.open_ticket(interaction)

    async def open_ticket(self, interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")

        if category is None:
            category = await guild.create_category("Tickets")

        ticket_channel = await category.create_text_channel(f"ticket-{interaction.user.name}")


        embed = discord.Embed(
            title="User melden",
            description=f"Hey, {interaction.user.mention}!\n\nWie können wir dir helfen? Ein Moderator wird in Kürze bei dir sein.\n\nWelchen Benutzer möchtest du melden?",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Ticket-System")

        message = await ticket_channel.send(embed=embed)

        await ticket_channel.send(f"{interaction.user.mention}, bitte geben Sie die User-ID des zu meldenden Benutzers an.")

