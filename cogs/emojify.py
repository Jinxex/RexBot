
from discord.commands import slash_command
from discord.ext import commands
class Emojify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojified_texts = {} 

    @slash_command(description='📊 × Starte eine emojify text!')
    async def emojify(self, ctx, *, text):
        emoji_text = ""

        for char in text.lower():
            if char.isalpha():
                emoji_text += f":regional_indicator_{char}: "
            elif char.isspace():
                emoji_text += "    "
            else:
                emoji_text += char

        await ctx.respond(emoji_text)


        self.emojified_texts[ctx.author.id] = emoji_text

def setup(bot):
    bot.add_cog(Emojify(bot))
