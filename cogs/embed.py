import discord
from discord.ext import commands
from discord.commands import slash_command


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Create an Embed")
    @discord.default_permissions(administrator=True, kick_members=True)
    @discord.guild_only()
    async def embed(self, ctx):
        if ctx.author.guild_permissions.administrator:
            modal = Modal(bot=self.bot, title="Create an Embed")
            await ctx.send_modal(modal)
        else:
            await ctx.response.send_message("Error: You do not have permission to execute this command.", ephemeral=True)


def setup(bot):
    bot.add_cog(Embed(bot))


class Modal(discord.ui.Modal):
    def __init__(self, bot, *args, **kwargs):
        self.bot = bot
        super().__init__(
            discord.ui.InputText(label="Embed Title", placeholder="Enter title"),
            discord.ui.InputText(
                label="Embed Description",
                placeholder="Enter text",
                style=discord.InputTextStyle.long,
            ),
            discord.ui.InputText(
                label="Embed Thumbnail",
                placeholder="Enter thumbnail URL, otherwise leave empty",
                style=discord.InputTextStyle.short,
                required=False,
            ),
            discord.ui.InputText(
                label="Embed Image",
                placeholder="Enter image URL, otherwise leave empty",
                style=discord.InputTextStyle.short,
                required=False,
            ),
            discord.ui.InputText(
                label="Channel ID",
                placeholder="Enter ID",
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
            f"Embed successfully created and sent in {channel.mention}!",
            ephemeral=True,
        )
