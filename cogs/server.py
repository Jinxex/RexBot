import discord
import ezcord
import datetime
import random
import asyncio
import json
import aiosqlite
import sqlite3
import os
import asyncpraw

from discord.ext import commands
from datetime import datetime
from discord.commands import slash_command, Option, SlashCommandGroup


class serverinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    info = SlashCommandGroup("info")

    @info.command(
        name="server",
        description="Zeigt Informationen Ã¼ber den server an."
    )
    async def _server(self, ctx: discord.Interaction):
        guild = ctx.guild
        name = str(ctx.guild.name)
        description = str(ctx.guild.description)
        guild = ctx.guild
        id = str(ctx.guild.id)
        memberCount = str(ctx.guild.member_count)
        text_channels = len(ctx.guild.text_channels)
        voice_channels = len(ctx.guild.voice_channels)
        categories = len(ctx.guild.categories)
        channels = text_channels + voice_channels
        role_count = len(ctx.guild.roles)
        emoji_count = len(ctx.guild.emojis)

        embed = discord.Embed(
            title=f"Server Information",
            color=discord.Color.blue()
        )
        embed.add_field(name=':crown: Owner', value=f'```{ctx.guild.owner}```', inline=False)
        embed.add_field(name=":people_hugging: Members", value=f"```{memberCount}```", inline=True)
        embed.add_field(name=":robot: Bots", value=f"```{sum(member.bot for member in ctx.guild.members)}```",
                        inline=True)
        embed.add_field(name=":id: Server ID", value=f"```{id}```", inline=False)
        embed.add_field(name=":calendar: Created", value=f"```{ctx.guild.created_at.__format__('%d.%m.%Y')}```",
                        inline=False)
        embed.add_field(name=":pencil2: Text Channels", value=f"```{text_channels}```", inline=True)
        embed.add_field(name=":microphone2: Voice Channels", value=f"```{voice_channels}```", inline=True)
        embed.add_field(name=":gem: Categories", value=f"```{categories}```", inline=True)
        embed.add_field(name=":shield: Roles", value=f"```{role_count}```", inline=True)
        embed.add_field(name=":sparkles: Boosts", value=f"```{ctx.guild.premium_tier}```", inline=True)
        embed.add_field(name=":chart_with_upwards_trend: Boost Level",
                        value=f"```{ctx.guild.premium_subscription_count}```", inline=True)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(serverinfo(bot))