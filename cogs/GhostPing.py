import discord
from discord.ext import commands
import asyncio
import ezcord
from discord.commands import slash_command

class GhostDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("database/ghost.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS ghost_ping(
            guild_id INTEGER PRIMARY KEY,
            status INTEGER DEFAULT 0
            )
            """
        )

    async def check_bot_settings(self, guild_id):
        result = await self.one("SELECT * FROM ghost_ping WHERE guild_id = ?", (guild_id,))
        if result is None:
            await self.execute("INSERT INTO ghost_ping (guild_id, status) VALUES (?, ?)", (guild_id, 0))
            result = await self.one("SELECT * FROM ghost_ping WHERE guild_id = ?", (guild_id,))
        return {"guild_id": result[0], "status": result[1]} if result else None

    async def update_bot_settings(self, guild_id, status):
        await self.execute("UPDATE ghost_ping SET status = ? WHERE guild_id = ?", (status, guild_id))

db = GhostDB()




class GhostPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        try:
            check_settings = await db.check_bot_settings(guild_id=message.guild.id)

            if isinstance(message.channel, discord.DMChannel):
                return

            if message.author.bot:
                return

            if check_settings["status"] != 0:
                if message.mentions:
                    if len(message.mentions) < 3:
                        for m in message.mentions:
                            if m != message.author and not m.bot:
                                embed = discord.Embed(
                                    title=f"👻 | Ghost ping",
                                    description=f"**{m.mention}**, you were ghost pinged by {message.author.mention}.\n\n**Message:** {message.content}",
                                    color=discord.Color.red()
                                )
                                await message.channel.send(embed=embed)
                    else:
                        embed = discord.Embed(
                            title=f"👻 | Ghost ping",
                            description=f"**{len(message.mentions)} Users** have been ghost pinged.\n\n**Message by {message.author.mention}:** {message.content}",
                            color=discord.Color.red()
                        )
                        await message.channel.send(embed=embed)
        except Exception as e:
            print(f"An error occurred: {e}")
    @slash_command(name="ghost-ping-settings", description="Enable or disable the ghost ping system!")
    async def ghost_ping_settings(self, ctx: discord.ApplicationContext):
       await ctx.defer(ephemeral=True)
       check_settings = await db.check_bot_settings(guild_id=ctx.guild.id)

       emb = discord.Embed(
           title="👻 | Configure the anti ghost ping system",
           description=f"Currently, the anti ghost ping system is {'**enabled**' if check_settings['status'] == 0 else '**disabled**'}. To {'**turn it off**' if check_settings['status'] == 0 else '**turn it on**'}, press the button below.",
           color=discord.Colour.blurple()
       )
       emb.set_footer(icon_url=ctx.guild.icon, text=f"{ctx.guild.name}")
       await ctx.respond(embed=emb, view=GhostPingButtons(check_settings), ephemeral=True)

def setup(bot):
    bot.add_cog(GhostPing(bot))

class GhostPingButtons(discord.ui.View):
    def __init__(self, check_settings):
        super().__init__(timeout=None)
        self.check_settings = check_settings

    @discord.ui.button(label="Toggle Ghost ping system", style=discord.ButtonStyle.blurple, custom_id="toggle_ghost_ping", row=1)
    async def toggle_ghost_ping(self, button, interaction):
        new_status = 0 if self.check_settings["status"] != 0 else 1
        await db.update_bot_settings(interaction.guild.id, new_status)

        emb = discord.Embed(
            title=f"👻 | You have successfully switched the ghost ping system {'**off**' if new_status != 0 else '**on**'}",
            description=f"The anti ghost ping system is now {'**disabled**' if new_status != 0 else '**enabled**'}. From now on, a message will be sent when a user mentions someone and deletes the message.",
            color=discord.Colour.green()
        )
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="cancel_ghost_ping", row=2)
    async def cancel_ghost_ping(self, button, interaction: discord.Interaction):
        emb = discord.Embed(
            title="👻 | Anti ghost ping system configuration canceled",
            description="The setting was successfully canceled, but you can change the settings at any time.",
            color=discord.Colour.red()
        )
        await interaction.response.edit_message(embed=emb, view=None)




