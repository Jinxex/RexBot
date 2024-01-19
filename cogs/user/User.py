import discord
from discord.ext import commands
from discord.commands import slash_command, Option


class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Show information about a user")
    @discord.guild_only()
    async def userinfo(
        self, ctx, user: Option(discord.Member, "Specify a user", default=None)
    ):
        if user is None:
            user = ctx.author

        embed = discord.Embed(
            title=f"Information about {user.name}",
            description=f"Here you can see all the details about {user.mention}",
            color=discord.Color.blue(),
        )

        time_created = discord.utils.format_dt(user.created_at, "R")
        time_joined = discord.utils.format_dt(user.joined_at, "R")

        embed.add_field(
            name="Name", value=f"{user.name}#{user.discriminator}", inline=False
        )
        embed.add_field(
            name="Nickname",
            value=f'{(user.nick if user.nick else "Not set")}',
            inline=False,
        )
        embed.add_field(name="Account created", value=time_created, inline=False)
        embed.add_field(name="Server joined", value=time_joined, inline=False)
        embed.add_field(
            name="Bot", value=f'{("Yes" if user.bot else "No")}', inline=False
        )
        embed.add_field(name="Roles", value=f"{len(user.roles)}", inline=False)
        embed.add_field(name="Top role", value=user.top_role.mention, inline=False)
        embed.add_field(name="Color", value=f"{user.color}", inline=False)
        embed.add_field(
            name="Booster",
            value=f'{("Yes" if user.premium_since else "No")}',
            inline=False,
        )

        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.name} • {ctx.author.id}")

        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(UserInfo(bot))
