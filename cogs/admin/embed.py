import discord
from discord.ext import commands
from discord.commands import slash_command


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Erstelle ein Embed")
    @commands.has_permissions(administrator=True)
    async def embed(self, ctx):
        modal = Modal(bot=self.bot, title="Erstelle ein Embed")
        await ctx.send_modal(modal)


def setup(bot):
    bot.add_cog(Embed(bot))


class Modal(discord.ui.Modal):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        super().__init__(
            discord.ui.InputText(label="Embed Titel", placeholder="Titel reinscheiben"),
            discord.ui.InputText(
                label="Embed Beschreibung",
                placeholder="Text reinschreiben",
                style=discord.InputTextStyle.long,
            ),
            discord.ui.InputText(
                label="Embed Thumbnail",
                placeholder="Thumbnail URL eintragen, ansonsten leer lassen",
                style=discord.InputTextStyle.short,
                required=False,
            ),
            discord.ui.InputText(
                label="Embed Image",
                placeholder="Image URL eintragen, ansonsten leer lassen",
                style=discord.InputTextStyle.short,
                required=False,
            ),
            discord.ui.InputText(
                label="Channel ID",
                placeholder="ID eintragen",
                style=discord.InputTextStyle.short,
            ),
            *args,
            **kwargs,
        )

    async def callback(self, interaction):
        embed = discord.Embed(
            title=self.children[0].value,
            description=self.children[1].value,
            color=discord.Color.green(),
        )
        thumbnail = self.children[2].value
        image = self.children[3].value
        channel_id = int(self.children[4].value)
        channel = self.bot.get_channel(channel_id)

        embed.set_thumbnail(url=thumbnail)
        embed.set_image(url=image)

        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"Embed erfolgreich in {channel.mention} erstellt und gesendet!",
            ephemeral=True,
        )
