import ezcord

class LanguageDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("utils/data/language.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS servers(
            server_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT '🇬🇧 English'
            )"""
        )

    async def get_server_language(self, server_id):
        result = await self.execute("SELECT language FROM servers WHERE server_id=?", (server_id,))
        return result['language'] if result else None

    async def set_server_language(self, server_id, language):
        await self.execute(
            "INSERT OR REPLACE INTO servers (server_id, language) VALUES (?, ?)",
            (server_id, language)
        )

class tempvoiceDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("utils/data/tempvoice.db")

    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            server_id INTEGER PRIMARY KEY,
            Category_id INTEGER DEFAULT 0,
            VoiceChannel_id INTEGER DEFAULT 0,
            Channel_id INTEGER DEFAULT 0
            )"""
        )

    async def get_channel(self, guild_id):
        await self.one("SELECT VoiceChannel_id FROM users WHERE server_id = ?",(guild_id))
    
    async def get_txtchannel(self, txt_channel,guild_id):
        async with self.start() as cursor:
            await cursor.execute("INSERT OR IGNORE INTO users (server_id) VALUES (?)", guild_id)
            await cursor.execute(f"UPDATE users SET Channel_id = ? WHERE server_id = ?", txt_channel,guild_id)


    async def get_voice(self, guild_id, voicechannel_id, category_id):
        async with self.start() as cursor:
            # Überprüfe, ob es einen Datensatz für den Server gibt und lege ihn an, falls nicht vorhanden
            await cursor.execute("INSERT OR IGNORE INTO users (server_id) VALUES (?)", (guild_id,))

            # Aktualisiere die VoiceChannel_id und Category_id für den Server
            await cursor.execute("UPDATE users SET VoiceChannel_id = ?, Category_id = ? WHERE server_id = ?", (voicechannel_id, category_id, guild_id))

class WelcomeDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("utils/data/db/wlc.db")

    async def setup(self):
        await self.exec("""
        CREATE TABLE IF NOT EXISTS servers (
        server_id INTEGER PRIMARY KEY,
        channel_id INTEGER DEFAULT 0,
        title TEXT,
        description TEXT,
        enabled TEXT DEFAULT Off,
        welcome_role INTEGER DEFAULT 0
        )
        """)

    async def add_welcome_role(self, server_id, role_id):
        await self.exec("UPDATE servers SET welcome_role = ? WHERE server_id = ?", role_id, server_id)

    async def get_welcome_role(self, server_id):
        return await self.one("SELECT welcome_role FROM servers WHERE server_id = ?", server_id)

    async def enable(self, server_id, channel_id, enabled):
        async with self.start() as cursor:
            await self.exec("INSERT OR IGNORE INTO servers (server_id) VALUES (?)", server_id)
            await self.exec("UPDATE servers SET channel_id = ? WHERE server_id = ?", channel_id, server_id)
            await self.exec("UPDATE servers SET enabled = ? WHERE server_id = ?", enabled, server_id)

    async def disable(self, server_id, enabled):
        async with self.start() as cursor:
            await self.exec("UPDATE servers SET enabled = ? WHERE server_id = ?", enabled, server_id)

    async def check_enabled(self, server_id):
        return await self.one("SELECT enabled FROM servers WHERE server_id = ?", server_id)

    async def channel_id(self, server_id):
        return await self.one("SELECT channel_id FROM servers WHERE server_id = ?", server_id)

    async def add_to_db(self, server_id):
        await self.exec("INSERT INTO servers (server_id) VALUES (?)", server_id)

    async def fix(self, server_id):
        await self.exec("INSERT OR IGNORE INTO servers (server_id) VALUES (?)", server_id)
        
class SternDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("utils/data/stern.db")


    async def setup(self):
        await self.execute(
            """CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            stern INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            Konto INTEGER DEFAULT 0
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
            "UPDATE users SET streak = ? WHERE user_id = ?", (streak or 0, user_id)
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
            await self.one("SELECT streak FROM users WHERE user_id = ? AND streak > 0", user_id)
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


    async def get_max_streak(self, user_id):
        return await self.one("SELECT MAX(streak) FROM users WHERE user_id = ?", user_id) or 0
    
    async def add_bonus_stern(self, user_id, bonus_stern):
        await self.execute(
            "UPDATE users SET stern = stern + ? WHERE user_id = ?", (bonus_stern, user_id)
        )