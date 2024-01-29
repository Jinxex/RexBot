import discord
import aiosqlite
from discord.commands import slash_command, Option
from discord.ext import commands


class WelcomeCard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DB = "welcome.db"

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                """CREATE TABLE IF NOT EXISTS welcome (
                    guild_id INTEGER,
                    welcome_channel INTEGER,
                    role_id INTEGER
                )"""
            )

    @slash_command()
    @discord.guild_only()
    async def welcome_setup(
        self, ctx: discord.ApplicationContext, channel: Option(discord.TextChannel), role_name: Option(discord.Role) 

    ):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute(
                "SELECT * FROM welcome WHERE guild_id = ?", (ctx.guild.id,)
            )
            entry = await cursor.fetchone()

            if entry:
                owner = ctx.guild.owner
                if owner:
                    await owner.send("Der Willkommens-Setup wurde bereits für diesen Server durchgeführt. Schreiben Sie dem littxle_, weil Sie den falschen Kanal oder die falsche Rolle eingegeben haben!")
                    await ctx.defer(ephemeral=True)
                    await ctx.respond("look at DM!", ephemeral=True)
                return
            

            await db.execute(
                "INSERT INTO welcome VALUES (?,?,?)", (ctx.guild.id, channel.id, role_name.id)
            )

            await db.commit()
            await ctx.defer(ephemeral=True)
            await ctx.respond(f"✅ Willkommenskanal auf {channel.mention} und Rollenname auf {role_name.mention} gesetzt", ephemeral=True)




    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async with aiosqlite.connect(self.DB) as db:
            cursor = await db.execute(
                "SELECT * FROM welcome WHERE guild_id = ?", (member.guild.id,)
            )
            entry = await cursor.fetchone()

            if entry:
                channel_id, role_id = entry[1], entry[2]
                channel = self.bot.get_channel(channel_id)
                role = member.guild.get_role(role_id)

                if channel and role:
                    embed = discord.Embed(
                        description=f"Hey {member.mention} und herzlich willkommen auf dem Discord-Server von **{member.guild.name}!**\n\n\n★ Du bist das {member.guild.member_count} Mitglied auf diesem Server!",
                        color=discord.Color.red(),
                    )
                    embed.set_author(
                        icon_url=member.guild.icon.url, name=member.guild.name
                    )
                    embed.set_image(
                        url="https://tse1.mm.bing.net/th?id=OIP.mJ4zvJuNlVIy_ryGKf_YpgHaC9&pid=Api&P=0&h=180"
                    )

                    await channel.send(member.mention, embed=embed)
                    await member.add_roles(role)



def setup(bot):
    bot.add_cog(WelcomeCard(bot))
