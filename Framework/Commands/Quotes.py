from discord.ext import commands
import discord
from ..GeneralUtilities.CommandAccess import CommandAccess
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
				embed.description = '> "' + content + '"\n'
				embed.description += " - " + author

			authorUser = await ctx.bot.fetch_user(int(author.lstrip("<@!").rstrip(">")))
			embed.set_thumbnail(url = (authorUser.avatar_url.BASE + authorUser.avatar_url._url))

			return embed


		if await CommandAccess.check_module_enabled("quotes") == False:
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		else:
			# Check if an ID is provided, if not get a random quote
			with open(Utilities.get_quotes_directory(), 'r') as f:
				data = json.load(f)

				maxIndex = 0
				for _ in data:
					maxIndex = maxIndex + 1
				maxIndex = maxIndex - 1
			if id == None:
				random = randint(0, maxIndex)
				author = data[random]["author"]
				content = data[random]["content"]

				embed = await prepareQuote(author, content, str(random))

			else:
				try:
					if int(id) < 0 or int(id) > maxIndex:
						embed.title = "Cannot get quote"
						embed.description = "Invalid quote ID. It must not be less than zero and must be less than the total number of quotes."
					else:
						content = data[int(id)]["content"]
						author = data[int(id)]["author"]
						embed = await prepareQuote(author, content, id)
				except ValueError:
					embed.title = "Cannot get quote"
					embed.description = "The quote ID must be a number."
				
		await ctx.send(embed = embed)

	@commands.command(name='totalQuotes')
	@commands.guild_only()
	async def totalQuotes(self, ctx):
		"""Get the total number of quotes available."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if await CommandAccess.check_module_enabled("quotes") == False:
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		else:
			with open(Utilities.get_quotes_directory(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1
			
			embed.title = "Total Quotes"
			embed.description = "I have " + str(maxIndex) + " quotes in my archives."
			embed.set_footer(text="Note, this is zero-indexed and counting starts at zero, not one.")
		await ctx.send(embed = embed)

	@commands.command(name='addQuote')
	@commands.guild_only()
	async def addQuote(self, ctx, quote:str, author:str):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if await CommandAccess.check_module_enabled("quotes") == False:
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		else:
			# TODO: noQuote checks will need to be here; also, will noQuote only prevent addQuote or other quote functions?
			with open(Utilities.get_quotes_directory(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			with open(Utilities.get_quotes_directory(), 'w') as f:
				quoteDictionary = {"content": quote , "author": author}
				data.append(quoteDictionary)
				json.dump(data, f, indent=4)
			
			embed.title = "Quote Added"
			embed.description = "The quote has been added to my archives as **Quote #" + str(maxIndex + 1) + ".**"
		await ctx.send(embed = embed)

	@commands.command(name='removeQuote')
	@commands.guild_only()
	async def removeQuote(self, ctx, id=None):
		"""Need to purge a quote? Use this. Only available to TitanBot Wizards."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if await CommandAccess.check_module_enabled("quotes") == False:
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_wizard(ctx) == None:
			embed.title = "Cannot use this command"
			embed.description = "You do not have access to use this command."
		else:
			if id == None:
				embed.title = "Failed to remove quote"
				embed.description = "You must pass a quote ID to remove."

			with open(Utilities.get_quotes_directory(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			try:
				if int(id) < 0 or int(id) > maxIndex:
					embed.title = "Failed to remove quote"
					embed.description = "You must pass a quote ID to remove."
				else:
					with open(Utilities.get_quotes_directory(), 'w') as f:
						data.remove(data[int(id)])
						json.dump(data, f, indent=4)
				
				embed.title = "Quote Removed"
				embed.description = "The quote has been purged from my archives. Total Quotes: **" + str(maxIndex - 1) + ".**"
			except ValueError:
				embed.title = "Failed to remove quote"
				embed.description = "The quote ID must be a number."

		await ctx.send(embed = embed)