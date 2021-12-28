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

		async def prepareQuote(author, content, id):
			embed.title = "Quote #" + id
			
			if "https://" in content:
				embed.set_image(url = content)
				embed.description = author
			else:
				embed.description = '> *"' + content + '"*\n'
				embed.description += " - " + author

			authorUser = await ctx.bot.fetch_user(int(author.lstrip("<@!").rstrip(">")))
			embed.set_thumbnail(url = (authorUser.avatar_url.BASE + authorUser.avatar_url._url))

			return embed


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
				random = randint(0, maxIndex)
				author = data[random]["author"]
				content = data[random]["content"]

				embed = await prepareQuote(author, content, str(random))

			else:
				try:
					if int(id) < 0:
						embed.title = "Cannot get quote"
						embed.description = "You must pass an ID that is not less than zero."
					elif int(id) > maxIndex:
						embed.title = "Cannot get quote"
						embed.description = "You are asking for a quote above the number of quotes I have."
					else:
						content = data[int(id)]["content"]
						author = data[int(id)]["author"]
						embed = await prepareQuote(author, content, id)
				except ValueError:
					embed.title = "Cannot get quote"
					embed.description = "You must pass a valid ID."
				
		await ctx.send(embed = embed)