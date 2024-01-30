import discord
from discord.ext import commands
from discord.commands import slash_command
import ezcord
import random
from ezcord import View

class role(ezcord.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(roleView())

    @slash_command(description="Hier ist ein Beispiel, wie man eine Rolle hinzufügt")
    async def role(self, ctx):
        embed_color = discord.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        embed = discord.Embed(
            title="Nico Ist besser als @Grift",
            description="du kannst nicht coden @Grift",
            color=embed_color
        )
        await ctx.respond(embed=embed, ephemeral=True, view=roleView())

def setup(bot):
    bot.add_cog(role(bot))

class roleView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Rolle", style=discord.ButtonStyle.blurple, row=1, custom_id="role_button")
    async def button_callback(self, button, interaction):
        role_name = 'neue Rolle'
        role = discord.utils.get(interaction.guild.roles, name=role_name)

        if role:
            member = interaction.guild.get_member(interaction.user.id)

            if role in member.roles:
                await interaction.response.send_message(f"Du hast bereits die Rolle {role_name}.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Du hast die Rolle {role_name} bekommen! Danke an Nico für den Code.", ephemeral=True)
                await member.add_roles(role)
        else:
            await interaction.response.send_message("Die Rolle wurde nicht gefunden. Stelle sicher, dass die Rolle existiert.", ephemeral=True)
