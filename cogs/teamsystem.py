import discord
from discord.ext import commands
from discord.commands import slash_command, SlashCommandGroup
import datetime
import cloudcord

class ranks(cloudcord.Cog, emoji="🌩"):
    print("test")
    team = SlashCommandGroup("team", description="Lass dich von niemandem bestehlen⭐")

    @team.command(name="uprank", description="Gib einem User einen Uprank!")
    async def uprank(self, interaction: discord.Interaction, channel: discord.TextChannel, member: discord.Member, oldrank: discord.Role, newrank: discord.Role, reason: str):
        if interaction.user.guild_permissions.administrator:
            embedVar = discord.Embed(title="**Uprank!**",
                                    description=f"**Teamler:** {member.mention}\n\n**Old Rank:** {oldrank.mention}\n\n**New Rank:** {newrank.mention}\n\n**Reason:** {reason}\n\n**Admin:** {interaction.user}",
                                    color=member.color,
                                    timestamp=datetime.datetime.now())
            embedVar.set_image(url="https://cdn.discordapp.com/attachments/1081906967729143873/1109228733749014638/Uprank.png")
            embedVar.set_thumbnail(url=member.display_avatar)
            msg = await channel.send(f"{member.mention}, Glückwunsch!", embed=embedVar)
            await interaction.response.send_message(content=f"Uprank gesendet in {msg.jump_url}", ephemeral=True)
            await member.send(f"Du wurdest auf dem Server({interaction.guild}) geuprankt! Glückwunsch!")
        else:
            embed = discord.Embed(title="**Error!**",
                                  description="Du hast keine Rechte diesen Command auszuführen.\nVielleicht nächstes mal...",
                                  timestamp=datetime.datetime.now())
            await interaction.response.send_message(embed=embed)

    @team.command(name="downrank", description="Gib einem User einen Downrank!")
    async def downrank(self, interaction: discord.Interaction, channel: discord.TextChannel, member: discord.Member,
                     oldrank: discord.Role, newrank: discord.Role, reason: str):
        if interaction.user.guild_permissions.administrator:
            embedVar = discord.Embed(title="**Downrank!**",
                                     description=f"**Teamler:** {member.mention}\n\n**Old Rank:** {oldrank.mention}\n\n**New Rank:** {newrank.mention}\n\n**Reason:** {reason}\n\n**Admin:** {interaction.user}",
                                     color=member.color,
                                     timestamp=datetime.datetime.now())
            embedVar.set_image(url="https://cdn.discordapp.com/attachments/1081906967729143873/1109228717403803779/Downrank.png")
            embedVar.set_thumbnail(url=member.display_avatar)
            msg = await channel.send(f"{member.mention}, mein Beileid!", embed=embedVar)
            await interaction.response.send_message(content=f"Downrank gesendet in {msg.jump_url}", ephemeral=True)
            await member.send(f"Du wurdest auf dem Server({interaction.guild}) gedownranked! Mein Beileid!")
        else:
            embed = discord.Embed(title="**Error!**",
                                  description="Du hast keine Rechte diesen Command auszuführen.\nVielleicht nächstes mal...",
                                  timestamp=datetime.datetime.now())
            await interaction.response.send_message(embed=embed)

    @team.command(name="team-kick", description="Gib einem User einen Team Kick!")
    async def team_kick(self, interaction: discord.Interaction, channel: discord.TextChannel, member: discord.Member,
                     oldrank: discord.Role, newrank: discord.Role, reason: str):
        if interaction.user.guild_permissions.administrator:
            embedVar = discord.Embed(title="**Team Kick!**",
                                     description=f"**Teamler:** {member.mention}\n\n**Old Rank:** {oldrank.mention}\n\n**New Rank:** {newrank.mention}\n\n**Reason:** {reason}\n\n**Admin:** {interaction.user}",
                                     color=member.color,
                                     timestamp=datetime.datetime.now())
            embedVar.set_image(url="https://cdn.discordapp.com/attachments/1081906967729143873/1109228698420383916/Team-Kick.png")
            embedVar.set_thumbnail(url=member.display_avatar)
            msg = await channel.send(f"{member.mention}, mein Beileid!", embed=embedVar)
            await interaction.response.send_message(content=f"Team Kick gesendet in {msg.jump_url}", ephemeral=True)
            await member.send(f"Du wurdest auf dem Server({interaction.guild}) aus dem Team geschmissen! Näachstes mal mehr anstrengen!")
        else:
            embed = discord.Embed(title="**Error!**",
                                  description="Du hast keine Rechte diesen Command auszuführen.\nVielleicht nächstes mal...",
                                  timestamp=datetime.datetime.now())
            await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(ranks(bot))
