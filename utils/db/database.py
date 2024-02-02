import ezcord

class LanguageDB(ezcord.DBHandler):
    def __init__(self):
        super().__init__("data/db/language.db")

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


