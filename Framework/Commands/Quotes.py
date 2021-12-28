from discord.ext import commands
import discord
from ..GeneralUtilities import CommandAccess


class Quotes(commands.Cog):
	
	@commands.command(name='quote')
	async def quote(self, ctx, id=None):
		"""Get a random quote, if an ID isn't provided."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		if await CommandAccess.CommandAccess.check_module_enabled("quotes") == False:
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		else:
			embed.description = "This module is not currently implemented yet... yeet"
		await ctx.send(embed = embed)
