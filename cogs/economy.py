import discord
from discord.ext import commands
import aiosqlite
import random
from discord.commands import SlashCommandGroup, Option


async def user_info(user_id: int):
    async with aiosqlite.connect("database/economy.db") as db:
        async with db.execute(
                "SELECT brownies FROM users WHERE user_id = ?", (user_id,)) as cursor:
            result = await cursor.fetchone()

        if result is None:
            return result

        return result[0]



class economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.DB = "database/economy.db"


    economy = SlashCommandGroup(name="economy")

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(BankButtons())

    @commands.Cog.listener()
    async def on_ready(self):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                msg_count INTEGER DEFAULT 0,
                brownies INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                kbb INTEGER DEFAULT 0,
                mbb INTEGER DEFAULT 0,
                gbb INTEGER DEFAULT 0,
                übt INTEGER DEFAULT 0
                )
                """
            )


    async def get_kbb(self, user_id, ctx):
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute("SELECT kbrowniebombe FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()

            if result is None:
                return result

            return result[0]






    async def get_msg(self, user_id, ctx):
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute("SELECT msg_count FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                if result is None:
                    return result

            return result[0]


    async def get_bank(self, user_id, ctx):
        async with aiosqlite.connect(self.DB) as db:
            async with db.execute("SELECT bank FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
            if result is None:
                return result

            return result[0]


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.author.id,)
            )
            await db.execute(
                "UPDATE users SET msg_count = msg_count + 1 WHERE user_id = ?", (message.author.id,)
            )
            await db.commit()


    @economy.command(description="Arbeite um dir leckere Brownies zu verdienen")
    @commands.cooldown(1, 21600, commands.BucketType.user)
    async def work(self, ctx):
        brownies = random.randint(5, 10)
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (ctx.author.id,)
            )
            try:
                await db.execute(
                    "UPDATE users SET brownies = brownies + ? WHERE user_id = ?", (brownies, ctx.author.id)
                )
                await db.commit()
                print(f"Updated brownies for user {ctx.author.id} successfully.")
            except Exception as e:
                print(f"Fehler beim hinzufügen der Brownies zum Profil von {ctx.author.id}. Error: {e}")
        embed = discord.Embed(
            title="Schicht beendet",
            description=f"Du hast gearbeitet und {brownies} Brownies bekommen.",
            color=discord.Color.random()
        )

        await ctx.respond(embed=embed)

    @economy.command(description="Hole dein Tagliches Brownie Geschenk ab")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        brownies = random.randint(40, 45)
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (ctx.author.id,)
            )
            try:
                await db.execute(
                    "UPDATE users SET brownies = brownies + ? WHERE user_id = ?", (brownies, ctx.author.id)
                )
                await db.commit()
                print(f"Updated brownies for user {ctx.author.id} successfully.")
            except Exception as e:
                print(f"Failed to update brownies for user {ctx.author.id}. Error: {e}")

            embed = discord.Embed(
                title="Daily reward",
                description=f"Du hast dein Daily Reward abgeholt und {brownies} Brownies erhalten.",
                color=discord.Color.random()
            )

            await ctx.respond(embed=embed)


    @economy.command(description="Zeige dir die Statistiken")
    async def stats(self, ctx):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (ctx.author.id,)
            )
        brownies = await user_info(ctx.author.id)
        msg = await self.get_msg(ctx.author.id, ctx)
        bank = await self.get_bank(ctx.author.id, ctx)

        embed = discord.Embed(
            title="Info",
            description=f"Hier sind deine Informationen {ctx.author.mention}",
            color=discord.Color.random()
        )
        embed.add_field(
            name="Deine Nachrichten",
            value=f"Du hast bereits **{msg}** Nachrichten gesendet.",
            inline=False
        )
        embed.add_field(
            name="Deine Brownies",
            value=f"Du hast dir durch deine harte Arbeit bereits **{brownies}** Brownies verdient.",
            inline=False
        )
        embed.add_field(
            name="Dein Bank account",
            value=f"Es werden gerade {bank} Brownies sicher auf deinem Bank account aufbewart.",
            inline=False
        )
        embed.set_thumbnail(url=ctx.author.display_avatar)

        await ctx.respond(embed=embed)


    @economy.command()
    @commands.cooldown(1, 21600, commands.BucketType.user)
    async def steal(self, ctx, user: Option(discord.Member)):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (ctx.author.id,)
            )
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user.id,)
            )
            brownies = await db.execute(
                "SELECT brownies FROM users WHERE user_id = ?", (ctx.author.id,)
            )
            await db.commit()
            opferbrownies = await db.execute("SELECT brownies FROM users WHERE user_id = ?", (user.id,))
            result = await opferbrownies.fetchone()


            geklaut = random.randint(4, 7)
            if result[0] >= geklaut:

                chance = random.randint(1, 10)

                if chance < 5:
                        await db.execute(
                            "UPDATE users SET brownies = brownies + ? WHERE user_id = ?", (geklaut, ctx.author.id)
                        )
                        await db.execute(
                            "UPDATE users SET brownies = brownies - ? WHERE user_id = ?", (geklaut, user.id)
                        )
                        await db.commit()
                        embed = discord.Embed(
                            title="<a:utility4:1192827960772796436> × Erfolg",
                            description=f"{ctx.author.mention} hat {user.mention} erfolgreich ausgeraubt"
                                        f" und dabei {geklaut} erbeutet",
                            color=discord.Color.random()
                        )
                        await ctx.respond(embed=embed)
                else:
                    embed = discord.Embed(
                        title="🛑 × Du wurdest erwischt",
                        description="Du must Strafe zahlen"
                    )
                    await ctx.respond(embed=embed)
            else:
                embed = discord.Embed(
                    title="🛑 × Stop",
                    description=f"Du kannst {user.mention} nicht ausrauben, **{user.name}** hat zu wenig Brownies",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed)


    @economy.command(description="Überweise einem anderen User brownies")
    async def überweisung(self,
                          ctx,
                          user: Option(discord.Member, required=True),
                          amount: Option(int, required=True),
                          message: Option(str, required=False)
                          ):
        authorbrow = await user_info(ctx.author.id)



        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (ctx.author.id,)
            )
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user.id,)
            )
            await db.commit()
            if authorbrow < amount:
                embed = discord.Embed(
                    title="❌  |  Stop",
                    description="**Du kleiner Schlingel** Du hast nicht genug Brownies um diese Überweisung zu tätigen.",
                    color=discord.Color.red()
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            await db.execute(
                "UPDATE users SET brownies = brownies + ? WHERE user_id = ?", (amount, user.id)
            )
            await db.execute(
                "UPDATE users SET brownies = brownies - ? WHERE user_id = ?", (amount, ctx.author.id)
            )
            await db.commit()

            brownies = await user_info(user.id)




        if ctx.author == user:
            embed = discord.Embed(
                title="❌  |  Stop",
                description="Du kannst dir nicht selber Brownies überweisen",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if message is not None:
            embed = discord.Embed(
                title="Brownie Überweisung🎉",
                description=f"{ctx.author.mention} hat {user.mention} **{amount}** Brownies überwiesen",
                color=discord.Color.random()
            )
            embed.add_field(
                name="Nachricht",
                value=f"```{message}```",
                inline=False
            )
            embed.set_footer(text=f"nun hat {user.name} {brownies} Brownies", icon_url=user.display_avatar)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="Brownie Überweisung🎉",
                description=f"{ctx.author.mention} hat {user.mention} **{amount}** Brownies überwiesen",
                color=discord.Color.random()
            )
            embed.set_footer(text=f"nun hat {user.name} {brownies} Brownies", icon_url=user.display_avatar)
            await ctx.respond(embed=embed)


    @economy.command()
    @commands.has_permissions(administrator=True)
    async def shop(self, ctx):
        embed = discord.Embed(
            title="Brownie Laden",
            description="Kaufe coole items im Shop",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="https://cdn.pixabay.com/photo/2017/03/13/23/28/icon-2141484_1280.png")
        select = ShopSelect(ctx.author.id)
        view = discord.ui.View()
        view.add_item(select)
        await ctx.respond(embed=embed, view=view)


    @economy.command(description="Zahle Brownies Auf dein Bankkonto einzahlen")
    @commands.has_permissions(administrator=True)
    async def bank(self, ctx):
        embed = discord.Embed(
            title="Bank account",
            description=f"Willkommen in deinem Bank account {ctx.author.mention} hier kannst du Brownies einzahlen"
                        "oder deine Brownies abheben.",
            color=discord.Color.random()
        )
        embed.add_field(
            name="Einzahlen",
            value="Du kannst maximal 100 Brownies auf dein Konto enzahlen, "
                  "um sie vor Dieben zu schützen",
            inline=False
        )

        await ctx.respond(embed=embed, view=BankButtons())


    @economy.command()
    async def use(self, ctx, item: Option(choices=["Kleine Brownie Bombe", "Mittlere Brownie Bombe"], required=True)):
        async with aiosqlite.connect(self.DB) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (ctx.author.id,)
            )
            await db.commit()

            if item == "Kleine Brownie Bombe":
                await db.execute(
                    "UPDATE users SET übt = übt - 1 WHERE user_id = ?", (ctx.author.id,)
                )
                await db.commit()


class Einzahlen_Modal(discord.ui.Modal):
    def __init__(self, brownies, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="einzahlen",
                placeholder="z.b. 50"
            ),
            brownies,
            *args,
            **kwargs
        )

    async def callback(self, interaction):
        async with aiosqlite.connect("database/economy.db") as db:
            await db.execute(
                "UPDATE users SET bank = bank + ? WHERE user_id = ?", (self.children[0].value, interaction.user.id)
            )
            await db.execute(
                "UPDATE users SET brownies = brownies - ? WHERE user_id = ?",
                (self.children[0].value, interaction.user.id)
            )
            await db.commit()
            embed = discord.Embed(
                title="👍 × Erfolg",
                description=f"Du hast erfogreich {self.children[0].value} Brownies auf dein Konto eingezahlt.",
                color=discord.Color.green()
            )
            await interaction.respond(embed=embed)


class Abheben_Modal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(
            discord.ui.InputText(
                label="abheben",
                placeholder="z.b. 60"
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction):
        async with aiosqlite.connect("database/economy.db") as db:
            brownies = await db.execute(
                "SELECT bank FROM users WHERE user_id = ?", (interaction.user.id,)
            )
            if brownies > 100:
                embed = discord.Embed(
                    title="❌ | Stop",
                    description="Du kleiner Schlingel, du hast bereits 100 Brownies auf deinem Konto.",
                    color=discord.Color.red()
                )
                await interaction.respond(embed=embed)
            await db.execute(
                "UPDATE users SET bank = bank - ? WHERE user_id = ?", (self.children[0].value, interaction.user.id)
            )
            await db.execute(
                "UPDATE users SET brownies = brownies + ? WHERE user_id = ?",
                (self.children[0].value, interaction.user.id)
            )
            await db.commit()
            embed = discord.Embed(
                title="👍 × Erfolg",
                description=f"Du hast erfogreich {self.children[0].value} Brownies avon deinem Konto abgehoben.",
                color=discord.Color.green()
            )
            await interaction.respond(embed=embed)





class BankButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.button(label="Einzahlen", emoji="🛬", custom_id="einzahlen", style=discord.ButtonStyle.primary)
    async def button_callback1(self, button, interaction):
        await interaction.response.send_modal(Einzahlen_Modal(title="Zahle Brownies in dein Bank account ein"))


    @discord.ui.button(label="Abheben", emoji="🛫", custom_id="ablehnen", style=discord.ButtonStyle.primary)
    async def button_callback2(self, button, interaction):
        await interaction.response.send_modal(Abheben_Modal(title="Hebe Brownies von deinem Bank account ab"))



class ShopSelect(discord.ui.Select):
    def __init__(self, user_id: int):
        super().__init__(
            min_values=1,
            max_values=1,
            placeholder="Kaufe ein Item",
            options=options,
            row=2
        )

        self.user_id = user_id

    async def callback(self, interaction):
        async with aiosqlite.connect("database/economy.db") as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (interaction.user.id,)
            )
            await db.commit()
            brownies = await user_info(interaction.user.id)
            if self.values[0] == "Kleine Brownie Bombe":

                if brownies >= 100:
                    await db.execute(
                        "UPDATE users SET kbb = kbb + 1 WHERE user_id = ?", (interaction.user.id,)
                    )
                    await db.execute(
                        "UPDATE users SET brownies = brownies - 100 WHERE user_id = ?", (interaction.user.id,)
                    )
                    await db.commit()
                    embed = discord.Embed(
                        title="👍  |  Kauf abgeschlossen",
                        description="Du hast erfolgreich eine **kleine Brownie Bombe** gekauft",
                        color=discord.Color.blue()
                    )
                    await interaction.respond(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌  |  Stop",
                        description="Du hast nicht genug Brownies um das Item kaufen zu können",
                        color=discord.Color.red()
                    )
                    await interaction.respond(embed=embed, ephemeral=True)
                    return


            if self.values[0] == "Mitlere Brownie Bombe":
                if brownies >= 400:
                    await db.execute(
                        "UPDATE users SET mbb = mbb + 1 WHERE user_id = ?", (interaction.user.id,)
                    )
                    await db.execute(
                        "UPDATE users SET brownies = brownies - 400 WHERE user_id = ?", (interaction.user.id,)
                    )
                    await db.commit()
                    embed = discord.Embed(
                        title="👍  |  Kauf abgeschlossen",
                        description="Du hast erfolgreich eine **Mitlere Brownie Bombe** gekauft",
                        color=discord.Color.blue()
                    )
                    await interaction.respond(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌  |  Stop",
                        description="Du hast nicht genug Brownies um das Item kaufen zu können",
                        color=discord.Color.red()
                    )
                    await interaction.respond(embed=embed, ephemeral=True)
                    return

            if self.values[0] == "Große Brownie Bombe":
                if brownies >= 950:
                    await db.execute(
                        "UPDATE users SET gbb = gbb + 1 WHERE user_id = ?", (interaction.user.id,)
                    )
                    await db.execute(
                        "UPDATE users SET brownies = brownies - 950 WHERE user_id = ?", (interaction.user.id,)
                    )
                    await db.commit()
                    embed = discord.Embed(
                        title="👍  |  Kauf abgeschlossen",
                        description="Du hast erfolgreich eine **Große Brownie Bombe** gekauft",
                        color=discord.Color.blue()
                    )
                    await interaction.respond(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌  |  Stop",
                        description="Du hast nicht genug Brownies um das Item kaufen zu können",
                        color=discord.Color.red()
                    )
                    await interaction.respond(embed=embed, ephemeral=True)
                    return

            if self.values[0] == "Überraschungstüte":
                if brownies >= 950:
                    await db.execute(
                        "UPDATE users SET übt = übt + 1 WHERE user_id = ?", (interaction.user.id,)
                    )
                    await db.execute(
                        "UPDATE users SET brownies = brownies - 400 WHERE user_id = ?", (interaction.user.id,)
                    )
                    await db.commit()
                    embed = discord.Embed(
                        title="👍  |  Kauf abgeschlossen",
                        description="Du hast erfolgreich eine **Überraschungstüte** gekauft",
                        color=discord.Color.blue()
                    )
                    await interaction.respond(embed=embed)
                else:
                    embed = discord.Embed(
                        title="❌  |  Stop",
                        description="Du hast nicht genug Brownies um das Item kaufen zu können",
                        color=discord.Color.red()
                    )
                    await interaction.respond(embed=embed, ephemeral=True)
                    return


options = [
    discord.SelectOption(label="Kleine Brownie Bombe", emoji="💣", description="Preis: 100"),
    discord.SelectOption(label="Mitlere Brownie Bombe", emoji="💣", description="Preis: 400"),
    discord.SelectOption(label="Große Brownie Bombe", emoji="💣", description="Preis: 950"),
    discord.SelectOption(label="Überraschungstüte", emoji="🛍️", description="Preis: 400")
]


def setup(bot):
    bot.add_cog(economy(bot))