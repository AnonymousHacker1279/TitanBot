from discord.ext import commands
import discord
from ..GeneralUtilities import CommandAccess
from ..GeneralUtilities import GeneralUtilities as Utilities
import json
from random import randint


class Quotes(commands.Cog):
	
	@commands.command(name='quote')
	@commands.guild_only()
	async def quote(self, ctx, id=None):
		"""Get a random quote, if an ID isn't provided."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		if await CommandAccess.CommandAccess.check_module_enabled("quotes") == False:
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		else:
			# Check if an ID is provided, if not get a random quote
			with open(Utilities.get_quotes_directory(), 'r') as f:
				data = json.load(f)

				maxIndex = 0
				for _ in data:
					maxIndex = maxIndex + 1
			if id == None:
				random = randint(0, maxIndex - 1)
				author = data[random]["author"]

				embed.title = "Quote #" + str(random)
				embed.description = '> *"' + data[random]["content"] + '"*\n'
				embed.description += " - " + author
			else:
				try:
					if int(id) <= 0:
						embed.title = "Cannot get quote"
						embed.description = "You must pass an ID above zero."
					elif int(id) > maxIndex - 1:
						embed.title = "Cannot get quote"
						embed.description = "You are asking for a quote above the number of quotes I have."
					else:
						embed.title = "Quote #" + id
						embed.description = '> *"' + data[int(id) - 1]["content"] + '"*\n'
						embed.description += " - " + data[int(id) - 1]["author"]
				except ValueError:
					embed.title = "Cannot get quote"
					embed.description = "You must pass a valid ID."
				
		await ctx.send(embed = embed)
