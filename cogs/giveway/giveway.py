import discord
from discord.commands import slash_command
import ezcord
from ezcord import View
from discord.ext import commands
import random

class givewayDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("data/db//giveway.db")


    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            Giveway_id INTEGER DEFAULT 0,
            Server_id INTEGER DEFAULT 0,
            Mesaage_id INTEGER DEFAULT 0,
            )"""
        )


class giveway(ezcord.Cog):



    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(GiveawayView())

    

    @slash_command(description="🎉・Activate the GiveWay system")
    async def giveway(self, ctx):

        embed= discord.Embed(
            title="Giveaway start",
            description="🎉・Start a Giveaway System"
        )
        color=discord.Color.random()

        await ctx.respond(embed=embed, view=GiveawayView())



def setup(bot):
    bot.add_cog(giveway(bot))



class GiveawayModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Giveway",
                placeholder="Enter a win",
                min_length=1,
                max_length=25,
            ),
            title="a win?"
        )

    async def callback(self, interaction):
        giveway = self.children[0].value
        giveway_embed = discord.Embed(
            title=f"You have your {giveway} start",
            description=f"",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=giveway_embed, ephemeral=True)

class GiveawayView(View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label="Join the Giveway", style=discord.ButtonStyle.green, row=1, custom_id="Join_button")
    async def callback(self, button, interaction):
        await interaction.response.send_message("you are now in the **Giveaway**", ephemeral=True)


    @discord.ui.button(label="Leave the Giveway", style=discord.ButtonStyle.red , row=1, custom_id="Leave_button")
    async def callback1(self, button, interaction):
        await interaction.response.send_message("you have left the **Giveaway**", ephemeral=True)
