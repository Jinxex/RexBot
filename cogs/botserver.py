import discord
from discord.ext import commands
from discord.ext.commands import slash_command


class BotServer(commands.Cog):
    def __init__(self, ace):
        self.ace = ace

    @slash_command(description="Erhalte Informationen über den Server des Bots")
    async def server_bot(self, ctx):
        if ctx.guild:
            server = ctx.guild
            if ctx.author.permissions.administrator:
                embed = discord.Embed(
                    title="Server-Information", color=discord.Color.blue()
                )
                embed.add_field(name="Server Name", value=server.name, inline=False)
                embed.add_field(name="Server ID", value=server.id, inline=False)
                embed.add_field(
                    name="Mitgliederzahl", value=server.member_count, inline=False
                )
                embed.add_field(
                    name="Kanalanzahl", value=len(server.channels), inline=False
                )

                await ctx.respond(embed=embed, ephemeral=True)
            else:
                await ctx.respond(
                    "Du hast keine Berechtigung, diesen Befehl zu verwenden."
                )
        else:
            await ctx.respond(
                "Dieser Befehl kann nur in einem Server verwendet werden.",
                ephemeral=True,
            )


def setup(ace):
    ace.add_cog(BotServer(ace))
