import discord
from discord.commands import slash_command
from ezcord import View
from discord.ext import commands
import random

class GiveawayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_started = False
        self.giveaway_embed = None

    def create_giveaway_embed(self, giveaway_name):
        embed_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        return discord.Embed(
            title=f"🎉 Giveaway: {giveaway_name}",
            description=f"You can win {giveaway_name}!",
            color=embed_color
        )

    async def start_giveaway(self, giveaway_name):
        self.giveaway_started = True
        self.giveaway_embed = self.create_giveaway_embed(giveaway_name)

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(GiveawayView())

    @slash_command(description="🎉・Activate the Giveaway system")
    async def giveaway(self, ctx):
        if not self.giveaway_started:
            await self.start_giveaway("Your Prize Name")
            modal = GiveawayModal(title="Create a Giveaway Embed")
            await ctx.send_modal(modal)
            await ctx.respond(embed=self.giveaway_embed, view=GiveawayView())
        else:
            await ctx.respond("Giveaway has already started.")

def setup(bot):
    bot.add_cog(GiveawayCog(bot))

class GiveawayModal(discord.ui.Modal):
    def __init__(self,  *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="Giveaway",
                placeholder="Enter a prize name",
                min_length=1,
                max_length=25,
            ),
            title="Create a Giveaway"
        )
    async def callback(self, interaction):
        giveway_name = self.children[0].value
        await interaction.response.send_message(f"🎉 Giveaway started: {giveway_name}", ephemeral=True)

class GiveawayView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join the Giveaway", style=discord.ButtonStyle.green, row=1, custom_id="Join_button")
    async def join_callback(self, button, interaction):
        if self.cog.giveaway_started:
            await interaction.response.send_message("You have joined the **Giveaway**", ephemeral=True)
        else:
            await interaction.response.send_message("No active giveaway at the moment.", ephemeral=True)

    @discord.ui.button(label="Leave the Giveaway", style=discord.ButtonStyle.red, row=1, custom_id="Leave_button")
    async def leave_callback(self, button, interaction):
        await interaction.response.send_message("You have left the **Giveaway**", ephemeral=True)
