import asyncio
import sqlite3

import discord
from discord import slash_command
from discord.ext import commands


class WarnSystem(commands.Cog):
     def __init__(self, bot):
         self.bot = bot
         self.connection = sqlite3.connect('database/warnings.db')
         self.cursor = self.connection.cursor()
         self.create_table()

     def create_table(self):
         self.cursor.execute('''CREATE TABLE IF NOT EXISTS warnings (
                                 member_id INTEGER,
                                 reason TEXT
                             )''')
         self.connection.commit()

     @commands.Cog.listener()
     async def on_ready(self):
         await asyncio.sleep(1.3)

     @slash_command(name="warn", description="Warn a user")
     @commands.has_permissions(administrator=True)
     async def warn(self, ctx, member: discord.Member, reason=None):
         # Assuming you have a database connection in self.connection
         cursor = self.connection.cursor()
         cursor.execute('INSERT INTO warnings (member_id, reason) VALUES (?, ?)', (member.id, reason))
         self.connection.commit()

         embed = discord.Embed(title=f'{member.mention} was warned.', description=f'Reason: **{reason}**')
         embed.set_author(name=member.display_name, icon_url=member.avatar.url)

         await ctx.respond(embed=embed)

     @slash_command(name="warnings", description="Show all warnings for a user")
     @discord.default_permissions(administrator=True)
     async def warnings(self, ctx, member: discord.Member):
         self.cursor.execute('SELECT reason FROM warnings WHERE member_id = ?', (member.id,))
         result = self.cursor.fetchall()

         if result:
             embed = discord.Embed(title=f'Warnings for {member.name}', color=discord.Color.red())
             for idx, row in enumerate(result):
                 embed.set_author(name=member.name, icon_url=member.avatar.url)
                 embed.add_field(name=f'Warning {idx + 1}', value=row[0], inline=False)
             await ctx.respond(embed=embed)
         else:
             embed2 = discord.Embed(title=f'There are no warnings for {member.name}', color=discord.Color.green())
             embed2.set_author(name=member.name, icon_url=member.avatar.url)
             await ctx.respond(embed=embed2)

     @slash_command(name="warning_leaderboard", description="Show warning leaderboard")
     @discord.default_permissions(administrator=True)
     async def leaderboard(self, ctx):
         self.cursor.execute('SELECT member_id, COUNT(*) FROM warnings GROUP BY member_id ORDER BY COUNT(*) DESC')
         result = self.cursor.fetchall()

         if result:
             embed = discord.Embed(title='Warning Leaderboard', color=discord.Color.gold())
             for idx, row in enumerate(result):
                 member = ctx.guild.get_member(row[0])
                 warnings_count = row[1]
                 embed.add_field(name=f'Place {idx + 1}: {member.name}', value=f'Number of warnings: {warnings_count}',
                                 inline=False)
             await ctx.respond(embed=embed)
         else:
             await ctx.respond('No warnings found on this server.')

     @slash_command(name="clear_warnings", description="Clear all warnings for a user")
     @discord.default_permissions(administrator=True)
     async def clear_warnings(self, ctx, member: discord.Member):
         self.cursor.execute('DELETE FROM warnings WHERE member_id = ?', (member.id,))
         self.connection.commit()
         await ctx.respond(f'Warnings for {member.mention} have been cleared.')


def setup(bot):
     bot.add_cog(WarnSystem(bot))