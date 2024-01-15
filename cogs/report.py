import discord
from discord.commands import slash_command, Option
import littxlecord
from discord.ext import commands
from littxlecord import View

class Report(littxlecord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = 817435791079768105


    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(reportView())



    @slash_command(
        description="Send a DM owner report about the bot!"
    )
    async def report(self, ctx, reason: Option(str, description="Describe your problem in more detail and where the error lies")):
        owner_user = await self.bot.fetch_user(self.owner_id)

        embed = discord.Embed(
            title=f"Report from {ctx.author.display_name}",
            description=reason,
            color=discord.Color.red()
        )

        dm_channel = await owner_user.create_dm()
        await dm_channel.send(embed=embed,view=reportView())

        await ctx.respond("Your report has been sent. Thank you, it may take a maximum of a day to receive an answer!", ephemeral=True)

def setup(bot):
    bot.add_cog(Report(bot))

class reportView(View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label="yes", style=discord.ButtonStyle.primary, emoji="✔", custom_id="yes", row=2)
    async def button_callback1(self, button, interaction):
        await interaction.response.send_message("Your error has been confirmed. Please join the Discord server for the bug role: https://discord.gg/8ew7Sw6Tzy", ephemeral=True)
    

    @discord.ui.button(label="no", style=discord.ButtonStyle.primary, emoji="❌", custom_id="no", row=2)
    async def button_callback2(self, button, interaction):
        await interaction.response.send_message("The bot owner didn't confirm it, which means it's not a bot bug, but a bug on the Discord server or wherever Discord is located and there's nothing we can do about it. Have fun!🥰")
    

