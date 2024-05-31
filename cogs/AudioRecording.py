import discord
from discord.ext import commands
from discord import slash_command
import ezcord

async def end_recording(sink: discord.sinks.AudioData, channel: discord.TextChannel):
    await sink.vc.disconnect()
    files = []
    for user_id, audio in sink.audio_data.items():
        member = channel.guild.get_member(user_id)
        username = member.display_name if member else f"User-{user_id}"
        files.append(discord.File(audio.file, f"{username}.{sink.encoding}"))

    await channel.send(files=files)




class recording(ezcord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc = None


    @ezcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(StopRecordingView(self.vc))

    @slash_command(description="🐼 • only take recordings when necessary!")
    async def record(self, ctx: discord.ApplicationContext):
        if not ctx.user.voice or not ctx.user.voice.channel:
            await ctx.defer(ephemeral=True)
            await ctx.respond("You are not in a voice channel!")
            return

        vc = await ctx.user.voice.channel.connect()
        print("join")
        vc.start_recording(discord.sinks.WaveSink(), end_recording, ctx.channel)
        embed = discord.Embed(
            title="⏺️•Recording",
            description=" 🐼 •Thank you for your trust. We are now recording your conversations. \n All conversations are recorded and sent to the team",
            colour=discord.Color.red()
        )
        await ctx.response.defer(ephemeral=True)
        await ctx.respond(embed=embed,view=StopRecordingView(vc))


def setup(bot):
    bot.add_cog(recording(bot))






class StopRecordingView(discord.ui.View):
    def __init__(self, vc):
        self.vc = vc
        super().__init__(timeout=None)


    @discord.ui.button(label="Stop", emoji="🔴", custom_id="stop")
    async def callback(self, _, interaction: discord.Interaction):
        if self.vc is None:
            await interaction.response.defer()
            await interaction.followup.send("The bot is not recording or is not in a voice channel!", ephemeral=True)
        else:
            self.vc.stop_recording()
            self.disable_all_items()
            await interaction.edit(view=self)

        await interaction.edit(view=self)