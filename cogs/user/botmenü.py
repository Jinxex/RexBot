
import discord
from discord.ext import commands
import ezcord
from discord.commands import slash_command

options = [
    discord.SelectOption(label="Owner", emoji="👑", value="owner"),
    discord.SelectOption(label="Support Server", emoji="🛠", value="support"),
    discord.SelectOption(label="Invite Bot", emoji="📎", value="invite"),
    discord.SelectOption(label="Server Count", emoji="🌐", value="server"),
    discord.SelectOption(label="Bot Feedback", emoji="⭐", value="Feedback"),
    discord.SelectOption(label="Help", emoji="🤖", value="help"),
]

class BotMenu(ezcord.Cog, emoji="🤖"):

    @ezcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(BotView())



    @ezcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(BotMenuSelectView(self.bot))


    
    @slash_command(description="This is an Bot menu")
    async def botinfo(self, ctx):
        
        embed = discord.Embed(
            title="🤖 Bot Menu Unlocked 🤖",
            description=f"Welcome to the Bot Menu! Select an option below.",
            color=discord.Color.orange()
        )

        await ctx.respond(embed=embed, view=BotMenuSelectView(self.bot))

def setup(bot):
    bot.add_cog(BotMenu(bot))

class BotMenuSelectView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.select(
        custom_id="haha",
        min_values=1,
        max_values=2,
        placeholder="Make a selection",
        options=options
    )
    async def callback(self, select, interaction: discord.Interaction):
        selected_option = select.values[0]
        await interaction.message.edit(view=self)
        if selected_option == "owner":
            owner_embed = discord.Embed(
                title="👑 Owner Confirmation",
                description="You can contact me on Discord at littxle_! ✨",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=owner_embed)
        elif selected_option == "support":
            support_embed = discord.Embed(
                title="🛠 • Support Confirmation",
                description="Here is my Support Server! • 🛠 [Join Now](https://discord.gg/6qQpTWzczY)",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=support_embed)
        elif selected_option == "invite":
            invite_embed = discord.Embed(
                title="📎 • Invite Confirmation",
                description="📎 • Invite me to your server! 📎 •  [Invite Now](https://discord.com/api/oauth2/authorize?client_id=1170449421796900925&permissions=8&scope=applications.commands+bot)",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=invite_embed)
        elif selected_option == "server":
            server_embed = discord.Embed(
                title="🌐 • Server Count",
                description=f"I'm currently in {len(self.bot.guilds)} servers.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=server_embed)
        elif selected_option == "Feedback":
            feedback_embed = discord.Embed(
                title="Feedback 🌟",
                description="Please Give Bot choose 1 to 5 stars for your feedback. \n"
                            "1 ⭐ - Poor\n"
                            "2 ⭐⭐ - Not so good\n"
                            "3 ⭐⭐⭐ - Average\n"
                            "4 ⭐⭐⭐⭐ - Good\n"
                            "5 ⭐⭐⭐⭐⭐ - Excellent",
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=feedback_embed, view=BotView())
        elif selected_option == "help":
            help_embed = discord.Embed(
                title="🤖 • Help Menu",
                description="Hey there! If you type /help, you'll see a list of my commands.",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=help_embed)


class BotView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="star 1", style=discord.ButtonStyle.gray, emoji="⭐", custom_id="star1_button")
    async def callback1(self, button, interaction):
        await interaction.response.send_modal(StarModal(title="Give me Feedback", stars="⭐"))

    @discord.ui.button(label="star 2", style=discord.ButtonStyle.gray, emoji="⭐", custom_id="star2_button")
    async def callback2(self, button, interaction):
        await interaction.response.send_modal(StarModal(title="Give me Feedback", stars="⭐⭐"))

    @discord.ui.button(label="star 3", style=discord.ButtonStyle.green, emoji="⭐", custom_id="star3_button")
    async def callback3(self, button, interaction):
        await interaction.response.send_modal(StarModal(title="Give me Feedback", stars="⭐⭐⭐"))

    @discord.ui.button(label="star 4", style=discord.ButtonStyle.blurple, emoji="⭐", custom_id="star4_button")
    async def callback4(self, button, interaction):
        await interaction.response.send_modal(StarModal(title="Give me Feedback", stars="⭐⭐⭐⭐"))

    @discord.ui.button(label="star 5", style=discord.ButtonStyle.danger, emoji="⭐", custom_id="star5_button")
    async def callback5(self, button, interaction):
        await interaction.response.send_modal(StarModal(title="Give me Feedback", stars="⭐⭐⭐⭐⭐"))

class StarModal(discord.ui.Modal):
    def __init__(self, stars, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Feedback",
                placeholder="Placeholder",
            ),
            discord.ui.InputText(
                label="Feedback Description",
                placeholder="Placeholder",
                style=discord.InputTextStyle.long,
            ),
            *args,
            **kwargs
        )
        self.stars = stars

    async def callback(self, interaction):
        channel_id = 1204138508256546866  #deine id

        channel = interaction.guild.get_channel(channel_id)
        if channel:
            embed = discord.Embed(
                title = f"📝 {self.children[0].value}",
                description = f"🌟 {self.children[1].value}, Bewertung: {self.stars} ⭐",
                color = discord.Color.gold()
            )
            await interaction.response.send_message("Thank you for your feedback, it was sent successfully", ephemeral=True)
            await channel.send(embed=embed)
