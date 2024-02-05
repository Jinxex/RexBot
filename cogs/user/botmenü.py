import discord
from discord.ext import commands
from discord.commands import slash_command
import asyncio
options = [
    discord.SelectOption(label="Owner", emoji="👑", value="owner"),
    discord.SelectOption(label="Support Server", emoji="🛠", value="support"),
    discord.SelectOption(label="Invite Bot", emoji="📎", value="invite"),
    discord.SelectOption(label="Server Count", emoji="🌐", value="server"),
    discord.SelectOption(label="Rate Bot", emoji="⭐", value="rate"),
]

class botmenu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="This is an owner menu")
    async def botinfo(self, ctx):
        select = BotMenu(bot=self.bot)

        view = discord.ui.View(timeout=None)
        view.add_item(select)

        embed = discord.Embed(
            title="🤖 Bot Menu Unlocked 🤖",
            description=f"Welcome to the Bot Menu! Select an option below.\n\nCurrently in {len(self.bot.guilds)} servers.",
            color=discord.Color.orange()
        )

        await ctx.respond(embed=embed, view=view)

class BotMenu(discord.ui.Select):
    def __init__(self, bot):
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="Select an option",
            options=options
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]

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
        elif selected_option == "rate":
            await self.rate_bot(interaction)

    async def rate_bot(self, interaction: discord.Interaction):
        await interaction.response.send_message("Please rate the bot on a scale of 1 to 5 stars:\n\n```rate\nYour rating here\n```")

        try:
            rating_message = await self.bot.wait_for(
                "message",
                timeout=300,
                check=lambda message: message.author == interaction.user and message.channel == interaction.channel
            )

            try:
                stars = int(rating_message.content)
                if 1 <= stars <= 5:
                    star_text = get_stars(stars)
                    rating_embed = discord.Embed(
                        title="⭐ Bot Rating",
                        description=f"**From:** {interaction.user.mention}\n\n{star_text}",
                        color=discord.Color.gold()
                    )
                    await interaction.followup.send(embed=rating_embed)
                else:
                    await interaction.followup.send("Please provide a rating between 1 and 5.")
            except ValueError:
                await interaction.followup.send("Invalid rating. Please provide a number between 1 and 5.")
        except asyncio.TimeoutError:
            await interaction.followup.send("Sorry, the rating submission timed out. Please try again later.")

def get_stars(stars):
    if stars == 1:
        star_text = f"`⭐` Stern"
    else:
        star_text = f"`⭐" + " ⭐" * (stars - 1) + f"` Sterne"
    return star_text

def setup(bot):
    bot.add_cog(botmenu(bot))
