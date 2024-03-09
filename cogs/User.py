from discord import slash_command
import discord
import ezcord
from ezcord import View


class Userinfo(ezcord.Cog, emoji="<:info:1147664192325812406>"):

    @slash_command(description="Get information about a user on the server")
    @discord.option("user", discord.Member, description="Select the user about whom the info should be")
    async def user(self, ctx: discord.ApplicationContext, member: discord.Member = None):
        if member is None:
            member = ctx.author
        if member not in ctx.guild.members:
            await ctx.respond("This user is not on the server", ephemeral=True)
            return
        if isinstance(member, discord.Member):
            activities = []
            for activity in member.activities:
                if isinstance(activity, discord.Spotify):
                    txt = f'Spotify: [{activity.artist} - {activity.title}]({activity.track_url})'
                elif isinstance(activity, discord.Game):
                    txt = f'Playing: {activity.name}'
                elif isinstance(activity, discord.Streaming):
                    txt = f'Streaming: [{activity.twitch_name} - {activity.game}]({activity.url})'
                elif isinstance(activity, discord.CustomActivity):
                    txt = f'Status: {activity.name}'
                else:
                    txt = f'{activity.name}: {activity.details}'
                activities.append(txt)
        rlist = []
        for role in member.roles:
            rlist.append(str(role.mention))
        rlist.reverse()
        embed = discord.Embed(title=f"memberinfo about {member.display_name}", color=0x5965f2)
        embed.add_field(name="Name:", value=f"{member}")
        embed.add_field(name="Nickname", value=f"{member.nick}" if member.nick else "has no nickname", inline=True)
        embed.add_field(name="Display Name", value=f"{member.display_name}")
        embed.add_field(name="Color", value=f"{member.colour}")
        embed.add_field(name="Mention", value=f"{member.mention}")
        embed.add_field(name='Status:', value=member.status, inline=False)
        embed.add_field(name="Booster",
                        value=f"Yes<t:{int(member.premium_since.timestamp())}:F>" if member.premium_since else "No")
        embed.add_field(name="Top Role", value=f"{member.top_role.mention}")
        embed.add_field(name="Bot:", value=f'{"Yes" if member.bot else "No"}')
        embed.add_field(name="Joined Server:", value=f"<t:{int(member.joined_at.timestamp())}:F>")
        embed.add_field(name="Joined Discord:", value=f"<t:{int(member.created_at.timestamp())}:F>")
        embed.add_field(name=f"Roles: {len(member.roles) - 1}", value=','.join(rlist), inline=False)
        embed.add_field(name="Timeout?", value="Yes" if member.timed_out else "No")
        banner_user = await self.bot.fetch_user(member.id)
        try:
            embed.set_image(url=banner_user.banner.url)
        except AttributeError:
            pass
        if activities:
            embed.add_field(name='Activities', inline=False, value='\n'.join(activities))
        embed.set_author(name=f"{member}", icon_url=f"{member.display_avatar}")
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_footer(text=f'Requested by {ctx.user.name} • {ctx.user.id}', icon_url=ctx.user.display_avatar)
        await ctx.respond(embed=embed, view=Userbutton(self, ctx, member, ctx.user))


def setup(bot: discord.Bot):
    bot.add_cog(Userinfo(bot))


class Userbutton(View):
    def __init__(self, bot, ctx, member, user) -> None:
        self.bot = bot
        self.ctx = ctx
        self.member = member
        self.user = user
        super().__init__(timeout=None)

    @discord.ui.button(label="🔰 Home", style=discord.ButtonStyle.green, custom_id="info")
    async def info(self, button, ctx: discord.Interaction):
        if self.member is None:
            self.member = self.ctx.author
        if isinstance(self.member, discord.Member):
            activities = []
            for activity in self.member.activities:
                if isinstance(activity, discord.Spotify):
                    txt = f'Spotify: [{activity.artist} - {activity.title}]({activity.track_url})'
                elif isinstance(activity, discord.Game):
                    txt = f'Playing: {activity.name}'
                elif isinstance(activity, discord.Streaming):
                    txt = f'Streaming: [{activity.twitch_name} - {activity.game}]({activity.url})'
                elif isinstance(activity, discord.CustomActivity):
                    txt = f'Status: {activity.name}'
                else:
                    txt = f'{activity.name}: {activity.details}'
                activities.append(txt)
        rlist = []
        for role in self.member.roles:
            rlist.append(str(role.mention))
        rlist.reverse()
        embed = discord.Embed(title=f"Memberinfo about {self.member.display_name}", color=0x5965f2)
        embed.add_field(name="Name:", value=f"{self.member}")
        embed.add_field(name="Nickname", value=f"{self.member.nick}" if self.member.nick else "has no nickname",
                        inline=True)
        embed.add_field(name="Display Name", value=f"{self.member.display_name}")
        embed.add_field(name="Color", value=f"{self.member.colour}")
        embed.add_field(name="Mention", value=f"{self.member.mention}")
        embed.add_field(name='Status:', value=self.member.status, inline=False)
        embed.add_field(name="Booster",
                        value=f"Yes<t:{int(self.member.premium_since.timestamp())}:F>" if self.member.premium_since else "No")
        embed.add_field(name="Top Role", value=f"{self.member.top_role.mention}")
        embed.add_field(name="Bot:", value=f'{"Yes" if self.member.bot else "No"}')
        embed.add_field(name="Joined Server:", value=f"<t:{int(self.member.joined_at.timestamp())}:F>")
        embed.add_field(name="Joined Discord:", value=f"<t:{int(self.member.created_at.timestamp())}:F>")
        embed.add_field(name=f"Roles: {len(self.member.roles) - 1}", value=','.join(rlist), inline=False)
        embed.add_field(name="Timeout?", value="Yes" if self.member.timed_out else "No")
        banner_user = await ctx.client.fetch_user(self.member.id)
        try:
            embed.set_image(url=banner_user.banner.url)
        except AttributeError:
            pass
        if activities:
            embed.add_field(name='Activities', inline=False, value='\n'.join(activities))
        embed.set_thumbnail(url=self.member.display_avatar)
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Avatar", style=discord.ButtonStyle.gray, custom_id="avatar")
    async def avatar(self, button, ctx: discord.ApplicationContext):
        if self.user.id != ctx.user.id:
            return await ctx.respond("You did not execute the command", ephemeral=True)
        embed = discord.Embed(title="Avatar of {}".format(self.member.display_name))
        embed.set_image(url=self.member.display_avatar)
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Banner", style=discord.ButtonStyle.blurple, custom_id="banner")
    async def banner(self, button, ctx: discord.Interaction):
        if self.user.id != ctx.user.id:
            return await ctx.respond("You did not execute the command", ephemeral=True)

        embed = discord.Embed(title="Banner of {}".format(self.member.display_name))
        if self.member.bot:
            embed.add_field(name=" ", value="Bots don't have banners")
            return await ctx.response.edit_message(embed=embed)
        banner_user = await ctx.client.fetch_user(self.member.id)
        try:
            embed.set_image(url=banner_user.banner.url)
        except AttributeError:
            embed.add_field(name=" ", value="This user doesn't have a banner")
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Permissions", style=discord.ButtonStyle.red, custom_id="permissions")
    async def permissions(self, button, ctx: discord.ApplicationContext):
        if self.user.id != ctx.user.id:
            return await ctx.respond("You did not execute the command", ephemeral=True)

        embed = discord.Embed(title="Permissions of {}".format(self.member.display_name))
        embed.add_field(name="Permissions",
                        value=",".join([str(perm[0]) for perm in self.member.guild_permissions if perm[1]]))
        await ctx.response.edit_message(embed=embed)

    @discord.ui.button(label="Roles", style=discord.ButtonStyle.blurple, custom_id="roles")
    async def roles(self, button, ctx: discord.ApplicationContext):
        if self.user.id != ctx.user.id:
            return await ctx.respond("You did not execute the command", ephemeral=True)
        rlist = []
        for role in self.member.roles:
            if role.name == "@everyone":
                continue
            rlist.append(str(role.mention))
        embed = discord.Embed(title="Roles of {}".format(self.member.display_name))
        if len(rlist) == 0:
            embed.add_field(name="Roles", value="This user has no roles")
            return await ctx.response.edit_message(embed=embed)
        embed.add_field(name=f"Roles: {len(self.member.roles) - 1}", value=','.join(rlist), inline=False)

        await ctx.response.edit_message(embed=embed)
