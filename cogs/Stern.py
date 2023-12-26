from discord.commands import slash_command, Option, SlashCommandGroup
from discord.ext import commands
import cloudcord
import discord
import random
import asyncio
from discord.ext import commands
from datetime import datetime


class sternDB(cloudcord.DBHandler):
    def __init__(self):
        super().__init__("stern.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            stern INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            Konto INTEGER DEFAULT 0,
            )"""
        )

    # db
    async def add_stern(self, user_id, stern=0):
        async with self.start() as cursor:
            await cursor.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,)
            )
            await cursor.execute(
                "UPDATE users SET stern = stern + ? WHERE user_id = ?", (stern, user_id)
            )

    async def subtract_stern(self, user_id, stern):
        await self.execute(
            "UPDATE users SET stern = CASE WHEN stern - ? < 0 THEN 0 ELSE stern - ? END WHERE user_id = ?",
            (stern, stern, user_id),
        )

    async def get_stern(self, user_id):
        return await self.one("SELECT stern FROM users WHERE user_id = ?", user_id) or 0

    async def get_streak(self, user_id):
        return (
            await self.one("SELECT streak FROM users WHERE user_id = ?", user_id) or 0
        )

    async def update_streak(self, user_id, streak):
        await self.execute(
            "UPDATE users SET streak = ? WHERE user_id = ?", (streak, user_id)
        )

    async def reset_streak(self, user_id):
        await self.execute("UPDATE users SET streak = 0 WHERE user_id = ?", user_id)

    async def subtract_stern(self, user_id, stern):
        await self.execute(
            "UPDATE users SET stern = CASE WHEN stern - ? < 0 THEN 0 ELSE stern - ? END WHERE user_id = ?",
            (stern, stern, user_id),
        )

        async def get_current_cash(self, user_id):
            return (
                await self.one("SELECT stern FROM users WHERE user_id = ?", user_id)
                or 0
            )

    async def check_streak(self, user_id):
        return (
            await self.one("SELECT streak > 0 FROM users WHERE user_id = ?", user_id)
            or False
        )

    async def add_stern(self, user_id, stern=0, to_account=False):
        async with self.start() as cursor:
            await cursor.execute(
                "INSERT OR IGNORE INTO users (user_id) VALUES(?)", (user_id,)
            )
            if to_account:
                await cursor.execute(
                    "UPDATE users SET Konto = Konto + ? WHERE user_id = ?",
                    (stern, user_id),
                )
            else:
                await cursor.execute(
                    "UPDATE users SET stern = stern + ? WHERE user_id = ?",
                    (stern, user_id),
                )

    async def get_konto(self, user_id):
        return await self.one("SELECT Konto FROM users WHERE user_id = ?", user_id) or 0

    async def update_konto(self, user_id, amount):
        await self.execute(
            "UPDATE users SET Konto = Konto - ? WHERE user_id = ?", (amount, user_id)
        )


db = sternDB()


class stern(cloudcord.Cog, emoji="⭐"):
    stern = SlashCommandGroup("stern", description="Lass dich von niemandem bestehlen⭐")

    # /daily commmad

    @stern.command(description="holt dir eine Belohnung ab")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        user_id = ctx.user.id

        current_streak = await db.get_streak(user_id)
        current_stern = random.randint(1, 60)

        if current_streak > 0 and await db.check_streak(user_id):
            current_streak += 1
            await db.update_streak(user_id, current_streak)
            message = f"Tägliche stern\nDu hast dir **{current_stern}** stern abgeholt! Sehr schmackhaft\n\nStreak: {current_streak} Tage - Streak beibehalten"
        else:
            await db.reset_streak(user_id)
            current_streak = 1
            await db.update_streak(user_id, current_streak)
            message = f"Tägliche stern\nDu hast dir **{current_stern}** stern abgeholt! Sehr schmackhaft\n\nStreak: {current_streak} Tag - Streak verloren"

        total_stern = await db.get_stern(user_id)
        await db.add_stern(user_id, current_stern)
        await db.close()

        embed = discord.Embed(
            title="Tägliche stern", description=message, color=discord.Color.yellow()
        )

        embed.set_footer(text=f"Du hast nun {total_stern + current_stern} stern ⭐")

        await ctx.respond(embed=embed)

    # /steal commmad

    @stern.command(
        description="Oh je, wenn du den Befehl befolgst, wirst du nie Freunde finden☹"
    )
    @commands.cooldown(1, 7200, commands.BucketType.user)
    async def steal(self, ctx, member: Option(discord.Member)):
        if member.id == ctx.author.id or member.id == ctx.bot.user.id:
            embed = discord.Embed(
                title="**Bruder warum**",
                description="Bruder aber warum versuchst du, dich selbst oder den Bot zu bestehlen?",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        success_chance = random.randint(1, 30)
        stolen_stern = random.randint(1, 100)
        total_stern_stealer = await db.get_stern(ctx.author.id)
        total_stern_victim = await db.get_stern(member.id)

        await db.subtract_stern(member.id, stolen_stern)
        await db.add_stern(ctx.author.id, stolen_stern)

        embed_stealer = discord.Embed(
            title="stern Diebstahl!",
            description=f"Du hast {stolen_stern} ⭐ von {member.mention} geklaut!",
            color=discord.Color.yellow(),
        )
        embed_stealer.set_footer(
            text=f"Du hast nun {total_stern_stealer + stolen_stern} stern ⭐"
        )

        embed_victim = discord.Embed(
            title="stern Diebstahl!",
            description=f"Deine stern wurde von {ctx.author.mention} gestohlen! 😢",
            color=discord.Color.red(),
        )
        embed_victim.set_footer(
            text=f"Du hast nun {max(0, total_stern_victim - stolen_stern)} stern ⭐"
        )

        await ctx.respond(embed=embed_stealer)
        await ctx.respond(embed=embed_victim)

    # /give commmad

    @stern.command(description="du kannst dich freunde machen")
    async def give(self, ctx, member: Option(discord.Member), amount: int, description):
        if member.id == ctx.author.id or member.id == ctx.bot.user.id:
            embed = discord.Embed(
                title="warum?",
                description="Warum versuchst du dich dazu, dich selbst oder den Bot was zu schenken?",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        if amount < 0:
            await ctx.respond(
                "Die Anzahl der stern  kann nicht kleiner als 0 sein.", ephemeral=True
            )
            return
        elif amount > 100:
            await ctx.respond(
                "Du kannst maximal 100 stern auf einmal geben.", ephemeral=True
            )
            return

        total_stern_sender = await db.get_stern(ctx.author.id)
        if total_stern_sender < amount:
            embed = discord.Embed(
                title="Du hast nicht genügend stern",
                description="Du hast nicht genügend stern, um diese Transaktion durchzuführen.",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return
        total_stern_receiver = await db.get_stern(member.id)

        if description != "du kannst nur 100 stern geben!":
            embed_sender = discord.Embed(
                title="stern übergaben",
                description=f"{ctx.author.mention} hat {amount} stern  an {member.mention} gegeben ⭐!",
                color=discord.Color.yellow(),
            )
            embed_sender.add_field(name="Grund", value=description)

        await db.subtract_stern(ctx.author.id, amount)
        await db.add_stern(member.id, amount)

        await ctx.respond(embed=embed_sender)

    # event commmad

    @stern.command(description="Löse ein zufälliges Event aus. uiii")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def event(self, ctx):
        stern = await db.one("SELECT stern FROM users WHERE user_id = ?", ctx.author.id)

        if stern is None:
            embed = discord.Embed(
                title="Oh, noch nicht registriert?",
                description="Dann mach es so schnell wie möglich /daily. Dann bist du bei uns registriert und hast Spaß mit deiner stern.",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed)
            return

        stern = int(stern)
        sterns_good = min(10, stern + random.randint(1, 7))
        sterns_not_good = max(0, min(30, stern - random.randint(1, 7)))
        goodordosent = random.randint(1, 2)
        user = ctx.guild.members
        eventgood = [
            f"Du hast eine Packung sterns auf der Straße gefunden du hast dich umgeschaut ob dich jemand "
            f"beobachtet... Als du festgestellt hat das dich niemand beobachtet hast du Lachend alle "
            f"sterns mitgenommen es waren **{sterns_good}** sterns.",
            f"Du hast im Aldilie eine stern "
            f"Packung geklaut allerdings hat dich "
            f"der Ladenbesitzer erwischt. Aber da "
            f"er mitleid hatte hast du "
            f"**{sterns_good}** sterns bekommen.",
            f"Du hast auf Onlysterns ein neues Video hochgeladen du wurdest allerdings gehackt aber du "
            f"konntest trozdem **{sterns_good}** sterns bekommen.",
            f"Du hast einer Alten Oma über die Straße geholfen. Aus ihrer Tasche sind wärendesen {sterns_good}"
            f" sterns gefallen. Du hast alle vor ihren Augen eingesammelt und bist abgehauen.",
            f"Du bist nach Hause gegangen und hast im Müll etwas stern Artiges gesehen du hast geschaut "
            f"und es waren tatsächlich **{sterns_good}** sterns im Müll du hollst alle raus und hast "
            f"jetzt **{sterns_good}** sterns mehr, da {sterns_good - 2} schlecht waren.",
            f"Du hast deine sterns gezählt wie jeden morgen weil am Tag vorher {random.choice(user)} da "
            f"war. Dann hast du festgestellt das sie/er/es dir **{sterns_good}** dagelassen hat",
            f"Du bist in den Wald gegangen und hast dort eine Kiste gefunden. In der Kiste waren "
            f"**{sterns_good}** sterns. Du hast sie genommen und bist abgehauen",
            f"Jemand hat dir **{sterns_good}** sterns geschenkt. Du hast dich gefreut und hast sie genommen",
            f"Jemand hat dich gefragt ob du **{sterns_good}** sterns haben willst oder ob er jemand anderen "
            f"doppelt geben soll. Du hast gesagt das du die sterns haben willst und hast sie bekommen",
            f"Eine Person hat dir **{sterns_good}** sterns geschenkt. Du hast dich gefreut und hast sie "
            f"genommen",
            f"Im Internet hast du eine Seite gefunden in der behauptet wurde das du **{sterns_good}** sterns "
            f"bekommen kannst. Du hast dich angemeldet und hast die sterns bekommen",
            f"In der Schule hast du einen stern gebacken und hast ihn mitgenommen. Als du ihn essen "
            f"wolltest hast du festgestellt das es **{sterns_good}** sterns waren",
            f"Die Oma die vorne an der Kasse war hat **{sterns_good}** sterns verloren. Du hast sie "
            f"aufgelesen und hast sie genommen",
        ]

        eventnotgood = [
            f"Du hast Elon Musk nach Twitter+ gefragt, er hatte dich mit seinem Waschbeken beworfen "
            f"und dir sind **{sterns_not_good}** sterns zerbrochen.",
            f"Du hast das neue Cyberpunk 2089 "
            f"gekauft allerdings ist es voller Bugs "
            f"und du ragest und zerbichst "
            f"**{sterns_not_good}** sterns dabei.",
            f"Du hast im Aldilie eine stern Packung geklaut allerdings hat dich der Ladenbesitzer "
            f"erwischt. Er hat dich verklagt und du musstest **{sterns_not_good}** sterns strafe zahlen.",
            f"Du bist auf den Bürgersteig hingefallen da du noch sterns in deiner Hosentasche hattest "
            f"sind **{sterns_not_good}** sterns rausgerollt und wurden von einem Auto überfahren",
            f"Du hast deine sterns gezählt wie jeden morgen weil am Tag vorher {random.choice(user)} "
            f"da war. Dann hast du festgestellt das sie/er/es dir **{sterns_not_good}** hinterhältig geklaut "
            f"hat!",
            f"Du bist zu McDonalds gegangen und hast dir einen McFlurry geholt. Als du "
            f"zurückkamst war dein McFlurry weg und du hast **{sterns_not_good}** sterns verloren.",
            f"{random.choice(user)} hat dir **{sterns_not_good}** sterns geklaut. Allerdings ist er "
            f"gestollpert und alle sind zerbrochen",
            f"Etwas hat dir **{sterns_not_good}** sterns geklaut. Du hast es nicht gesehen aber du hast "
            f"festgestellt das es ein Hund war. Du hast dich gefreut das es ein Hund war und hast "
            f"ihn weitergefüttert",
            f"Deine Mutter hat dir **{sterns_not_good}** sterns geklaut. Du hast sie gefragt warum sie das "
            f"getan hat. Sie hat gesagt das sie es für dich getan hat weil sie dich liebt. Du hast "
            f"dir gedacht das sie es für sich selbst getan hat und hast sie verprügelt "
            f"(that escalated quickly)",
            f"Alle deine sterns sind in der Waschmaschine gelandet. Du hast sie rausgeholt und alle "
            f"**{sterns_not_good}** sterns waren kaputt",
            f"Im Internet hast du eine Seite gefunden in der behauptet wurde das du **{sterns_not_good}** "
            f"sterns bekommen kannst. Du hast dich angemeldet und wurdest gescammt",
            f"Oben auf dem Dach hast du eine Kiste gefunden. In der Kiste waren **{sterns_not_good}** sterns. "
            f"Du hast sie genommen und hast sie runtergeworfen. Sie sind alle kaputt gegangen",
        ]
        sternembed = discord.Embed(
            title=f"{ctx.author.name} HAT stern!",
            description="Du hast Absofort " "stern...",
            color=discord.Color.red(),
        )

        eventgoodembed = discord.Embed(
            title=f"{ctx.author.name} ist etwas **gutes** passiert...",
            description=random.choice(eventgood),
            color=discord.Color.yellow(),
        )

        eventnotgoodembed = discord.Embed(
            title=f"{ctx.author.name} ist etwas **Schlechtes** passiert...",
            description=random.choice(eventnotgood),
            color=discord.Color.red(),
        )
        if int(stern) == 60:
            await ctx.respond(embed=sternembed)
            return
        if goodordosent == 1:
            await ctx.respond(embed=eventgoodembed)
            Neue_stern = stern + sterns_good
            await db.execute(
                "UPDATE users SET stern = ? WHERE user_id = ?",
                (Neue_stern, ctx.author.id),
            )
            return
        Neue_stern2 = stern - sterns_not_good
        await db.execute(
            "UPDATE users SET stern  = ? WHERE user_id = ?",
            (Neue_stern2, ctx.author.id),
        )
        await db.close()
        await ctx.respond(embed=eventnotgoodembed)

    @stern.command(description="Überweisen von stern auf konto")
    async def konto(self, ctx, amount: int):
        user_id = ctx.author.id

        current_stern = await db.get_stern(user_id)
        if amount <= 0 or amount > current_stern:
            await ctx.respond(
                "Ungültiger Betrag oder nicht genügend stern zum Überweisen.",
                ephemeral=True,
            )
            return
        await db.subtract_stern(user_id, amount)
        await db.add_stern(user_id, amount, to_account=True)

        embed = discord.Embed(
            title="stern auf das Konto überwiesen!",
            description=f"Sie haben erfolgreich {amount} stern auf Ihr Konto überwiesen!",
            color=discord.Color.yellow(),
        )
        await ctx.respond(embed=embed)



def setup(bot):
    bot.add_cog(stern(bot))
