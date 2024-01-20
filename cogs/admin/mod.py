import discord
from discord.commands import slash_command
from discord.ext import commands
import asyncio
import datetime
import aiosqlite
import time


class panel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="admin", description="Achtung der User wird immer für 24 Stunden timeout!"
    )
    @discord.default_permissions(administrator=True, kick_members=True)
    @discord.guild_only()
    async def punish(self, ctx, user: discord.Member, reason: str):
        overview_embed = discord.Embed(
            title=f"Wie möchtest du {user.name}#{user.discriminator} sanktionieren?",
            color=discord.Color.dark_red(),
        )
        overview_embed.add_field(name="", value=f" ", inline=False)
        overview_embed.add_field(
            name="joined server",
            value=user.joined_at.strftime("%d.%m.%Y %H:%M"),
            inline=True,
        )
        overview_embed.add_field(
            name="account created",
            value=user.created_at.strftime("%d.%m.%Y %H:%M"),
            inline=True,
        )
        overview_embed.add_field(name="Reason:", value=f"```{reason}```", inline=True)
        overview_embed.add_field(
            name="Was willst du mit ihm machen?", value=f" ", inline=False
        )
        overview_embed.set_thumbnail(url=user.avatar.url)
        overview_embed.set_footer(text=f"Timestamp: {datetime.datetime.utcnow()}")
        await ctx.respond(
            embed=overview_embed,
            view=PunishView(reason, user, timeout=86400),
            ephemeral=True,
        )
        await asyncio.sleep(10)
        await ctx.delete()


class PunishView(discord.ui.View):
    def __init__(self, reason, user, timeout=86400):
        super().__init__()
        self.reason = reason
        self.user = user
        self.timeout = timeout

    @discord.ui.button(
        label="Ban",
        style=discord.ButtonStyle.red,
        custom_id="ban",
        emoji="<a:banbutton:1086650068368633916>",
    )
    async def ban(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        if self.user.guild_permissions.ban_members:
            await interaction.followup.send(
                "Du kannst keine Moderatoren bannen.", ephemeral=True
            )
            await asyncio.sleep(5)
            return

        if self.user.id == interaction.user.id:
            await interaction.followup.send(
                "Du kannst dich nicht selbst bannen!", ephemeral=True
            )
            await asyncio.sleep(5)
            return

        if interaction.user.top_role.position < self.user.top_role.position:
            await interaction.followup.send(
                "Du kannst keinen Nutzer bannen, der eine höhere Rolle hat als du!",
                ephemeral=True,
            )
            await asyncio.sleep(5)
            return

        if interaction.user.guild_permissions.ban_members:
            await self.user.ban(reason=self.reason, delete_message_seconds=60000)
            await interaction.followup.send(
                f"{self.user.mention} wurde gebannt für `{self.reason}`", ephemeral=True
            )
            await asyncio.sleep(5)
            return

        if interaction.user.guild_permissions.ban_members:
            await interaction.followup.send(
                "Ohje.. du hast noch keine Berechtigung um Nutzer zu bannen!",
                ephemeral=True,
            )
            await asyncio.sleep(5)
            return

    @discord.ui.button(
        label="Kick",
        style=discord.ButtonStyle.blurple,
        custom_id="kick",
        emoji="<:KK_kick:1086663740038062081>",
    )
    async def kick(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.user.guild_permissions.kick_members:
            await interaction.response.send_message(
                "Du kannst keine Moderatoren kicken.", ephemeral=True
            )
            await asyncio.sleep(5)
            await interaction.delete_original_response()
            return

        if self.user.id == interaction.user.id:
            await interaction.response.send_message(
                "Du kannst dich nicht selbst kicken!", ephemeral=True
            )
            await asyncio.sleep(5)
            await interaction.delete_original_response()
            return

        if interaction.user.top_role.position < self.user.top_role.position:
            await interaction.response.send_message(
                "Du kannst keinen Nutzer kicken, der eine höhere Rolle hat als du!",
                ephemeral=True,
            )
            await asyncio.sleep(5)
            await interaction.delete_original_response()
            return

        if interaction.user.guild_permissions.kick_members:
            await self.user.kick(reason=self.reason)
            await interaction.response.send_message(
                f"{self.user.mention} wurde gekickt für `{self.reason}`", ephemeral=True
            )
            await asyncio.sleep(5)
            await interaction.delete_original_response()

    @discord.ui.button(
        label="timout",
        style=discord.ButtonStyle.blurple,
        custom_id="timeout",
        emoji="<:icon_bestrafung_timeout:987644033784483890>",
    )
    async def timeout(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        if self.user.guild_permissions.kick_members:
            await interaction.response.send_message(
                "Du kannst keine Moderatoren timeout geben", ephemeral=True
            )
            await asyncio.sleep(5)
            await interaction.delete_original_response()
            return

        if self.user.id == interaction.user.id:
            await interaction.response.send_message(
                "Du kannst dich nicht selbst timeout geben!", ephemeral=True
            )
            await asyncio.sleep(5)
            await interaction.delete_original_response()
            return

        if interaction.user.top_role.position < self.user.top_role.position:
            await interaction.response.send_message(
                "Du kannst keinen Nutzer timeout geben, der eine höhere Rolle hat als du!",
                ephemeral=True,
            )
            await asyncio.sleep(5)
            await interaction.delete_original_response()
            return
        until = datetime.now() + datetime.timedelta(seconds=self.timeout)

        await self.user.timeout(reason=self.reason, until=until)

        await interaction.response.send_message(
            f"{self.user.mention} wurde timeout für `{self.reason}`", ephemeral=True
        )
        await asyncio.sleep(5)
        await interaction.delete_original_response()

def setup(bot):
    bot.add_cog(panel(bot))
