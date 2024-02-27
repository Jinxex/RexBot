import discord
import ezcord

class inviter(ezcord.Cog):


    @ezcord.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(inviterbutton())

    @ezcord.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            integrations = await guild.integrations()
        except discord.Forbidden:
            return

        for integration in integrations:
            if isinstance(integration, discord.BotIntegration):
                if integration.application.user == self.bot.user:
                    try:
                        embed = discord.Embed(title="🎉 **Danke fürs Einladen!** 🎉", description="Wir freuen uns, dabei zu sein!", color=0xFF00FF)
                        embed.set_thumbnail(url=self.bot.user.avatar.url)
                        embed.add_field(name="Weitere Informationen", value="Dies ist eine automatisch generierte Nachricht.\nBitte zögern Sie nicht, uns bei Fragen zu kontaktieren.\nVielen Dank für Ihre Unterstützung! 💖", inline=False)
                        embed.set_footer(text="© 2024 Flexii")
                        
                        await integration.user.send(embed=embed,view=inviterbutton())
                    except discord.Forbidden:
                        return
                    break

def setup(bot):
    bot.add_cog(inviter(bot))




class inviterbutton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label="Support Server", style=discord.ButtonStyle.grey, row=1, emoji="🛠", custom_id="kaka")
    async def support_back(self, button, interaction):
        embed = discord.Embed(
            title="You can also use /bug to report a bug",
            description="If you want to support us on our Discord server, you can join\n  🛠 [Join Now](https://discord.gg/dgYCukrw3n) 🩷",
            color=discord.Color.orange()
        )
        await interaction.respond(embed=embed)



    



