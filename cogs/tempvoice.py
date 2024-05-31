import discord
import ezcord
import random
from discord.ext import commands, tasks
from discord.commands import slash_command


class TempvoiceDatabase(ezcord.DBHandler):
    def __init__(self):
        super().__init__("database/tempvoice.db")

    async def setup(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS channels (
        channel_id INTEGER PRIMARY KEY,
        owner_id INTEGER DEFAULT 0
        )
        """)

    async def add_channel(self, channel_id, owner_id):
        async with self.start() as cursor:
            await self.exec("INSERT OR IGNORE INTO channels (channel_id) VALUES (?)", channel_id)
            await self.exec("UPDATE channels SET owner_id = ? WHERE channel_id = ?", owner_id, channel_id)

    async def remove_channel(self, channel_id):
        await self.exec("DELETE FROM channels WHERE channel_id = ?", channel_id)

    async def return_owner(self, channel_id):
        return await self.one("SELECT owner_id FROM channels WHERE channel_id = ?", channel_id)

db = TempvoiceDatabase()
class Tempvoice(ezcord.Cog):

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(EditName())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        if before.channel is None and after.channel is not None:
            if after.channel.id ==1232:
                id = after.channel.category.id

                category = member.guild.get_channel(id)

                vc = await category.create_voice_channel(name=member.name)

                await member.move_to(vc)

                embed = discord.Embed(
                    title="👋 Willkommen in deinem eigenem Sprachkanal!",
                    description="Der Sprachkanal wurde außerdem automatisch auf **Privat** gestellt!"
                )
                await vc.send(embed=embed, view=EditName())

                await db.add_channel(channel_id=vc.id, owner_id=member.id)

                await vc.set_permissions(member.guild.default_role, view_channel=False)

def setup(bot: discord.Bot):
    bot.add_cog(Tempvoice(bot))

class EditName(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Name ändern",
        emoji="📝",
        custom_id="NameEditButton"
    )
    async def button_callback(self, button, interaction: discord.Interaction):
        owner_id = await db.return_owner(interaction.channel.id)
        if interaction.user.id == owner_id:
            await interaction.channel.edit(name="Button wurde geklickt")
            await interaction.response.send_message("channel ist nun neu name", ephemeral=True)
        else:
            await interaction.response.send_message("> **Du bist nicht der Inhaber dieses Tempchannels!**", ephemeral=True)


