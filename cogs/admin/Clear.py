import discord
from discord.ext import commands
from discord.commands import slash_command


class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Löscht Nachrichten")
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def clear(self, ctx, amount: int):
        if amount > 100:
            await ctx.respond(
                "Du kannst nicht mehr als 100 Nachrichten auf einmal löschen!"
            )
        else:
            count_members = {}
            messages_deleted = 0
            messages = await ctx.channel.history(limit=amount).flatten()

            for message in messages:
                if message.author in count_members:
                    count_members[message.author] += 1
                else:
                    count_members[message.author] = 1

            new_string = []

            for author, message_deleted in count_members.items():
                new_string.append(f"**{author}**: {message_deleted}")
                messages_deleted += message_deleted

            final_string = "\n".join(new_string)

            await ctx.channel.purge(limit=amount + 1)
            await ctx.respond(
                f"Es wurden {messages_deleted} Nachrichten gelöscht :white_check_mark: !\n\n{final_string}",
                ephemeral=True,
            )


def setup(bot):
    bot.add_cog(Clear(bot))
