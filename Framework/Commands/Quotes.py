from discord.errors import NotFound
from discord.ext import commands
import discord
from ..GeneralUtilities import CommandAccess
from ..GeneralUtilities import GeneralUtilities as Utilities
import json
from random import randint
import math


class Quotes(commands.Cog):

	@commands.command(name='quote')
	@commands.guild_only()
	async def quote(self, ctx, quoteID=None):
		"""Get a random quote, if an ID isn't provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		if not await CommandAccess.check_module_enabled("quotes"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "quotes"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "quote"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:

			async def prepare_quote(pAuthor, pContent, pId):
				embed.title = "Quote #" + pId

				if "https://" in pContent:
					embed.set_image(url=pContent)
					embed.description = pAuthor
				else:
					embed.description = '> "' + pContent + '"\n'
					embed.description += " - " + pAuthor

				try:
					authorUser = await ctx.bot.fetch_user(int(pAuthor.lstrip("<@!").rstrip(">")))
					embed.set_thumbnail(url=(authorUser.avatar_url.BASE + authorUser.avatar_url._url))
				except (NotFound, ValueError):
					embed.set_footer(text="Cannot get the profile picture for this user, try using a mention")

				return embed

			# Check if an ID is provided, if not get a random quote
			with open(Utilities.get_quotes_directory(), 'r') as f:
				data = json.load(f)

				maxIndex = 0
				for _ in data:
					maxIndex = maxIndex + 1
				maxIndex = maxIndex - 1
			if quoteID is None:
				random = randint(0, maxIndex)
				author = data[random]["author"]
				content = data[random]["content"]

				embed = await prepare_quote(author, content, str(random))

			else:
				try:
					if int(quoteID) < 0 or int(quoteID) > maxIndex:
						embed.title = "Cannot get quote"
						embed.description = "Invalid quote ID. It must not be less than zero and must be less than the " \
							"total number of quotes. "
					else:
						content = data[int(quoteID)]["content"]
						author = data[int(quoteID)]["author"]
						embed = await prepare_quote(author, content, quoteID)
				except ValueError:
					embed.title = "Cannot get quote"
					embed.description = "The quote ID must be a number."

		await ctx.send(embed=embed)

	@commands.command(name='totalQuotes')
	@commands.guild_only()
	async def total_quotes(self, ctx):
		"""Get the total number of quotes available."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("quotes"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "quotes"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "totalQuotes"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
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
		await ctx.send(embed=embed)

	@commands.command(name='addQuote')
	@commands.guild_only()
	async def add_quote(self, ctx, quote: str, author: str):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("quotes"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "quotes"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "addQuote"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			with open(Utilities.get_quotes_directory(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			with open(Utilities.get_quotes_directory(), 'w') as f:
				quoteDictionary = {"content": quote, "author": author}
				data.append(quoteDictionary)
				json.dump(data, f, indent=4)

			embed.title = "Quote Added"
			embed.description = "The quote has been added to my archives as **Quote #" + str(maxIndex + 1) + ".**"
		await ctx.send(embed=embed)

	@commands.command(name='removeQuote')
	@commands.guild_only()
	async def remove_quote(self, ctx, id=None):
		"""Need to purge a quote? Use this. Only available to TitanBot Wizards."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("quotes"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "quotes"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "removeQuote"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		elif await CommandAccess.check_user_is_wizard(ctx) is None:
			embed.title = "Cannot use this command"
			embed.description = "You do not have access to use this command."
		else:
			if id is None:
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
				embed.description = "The quote has been purged from my archives. Total Quotes: **" + str(
					maxIndex - 1) + ".**"
			except ValueError:
				embed.title = "Failed to remove quote"
				embed.description = "The quote ID must be a number."

		await ctx.send(embed=embed)

	@commands.command(name='searchQuotes')
	@commands.guild_only()
	async def search_quotes(self, ctx, quoteAuthor=None, page=1):
		"""Search quotes by author. Lists up to 5 per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		if not await CommandAccess.check_module_enabled("quotes"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "quotes"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "searchQuotes"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			# Check if an author was provided
			if quoteAuthor is None:
				embed.title = "Cannot search quotes"
				embed.description = "You must provide an author"
			quoteAuthor = str(quoteAuthor)

			# Get the quote data
			with open(Utilities.get_quotes_directory(), 'r') as f:
				data = json.load(f)

				maxIndex = 0
				# The quote index here lists all quote IDs associated with the author
				authorQuoteIndex = []
				for i in data:
					maxIndex = maxIndex + 1
					if quoteAuthor in i['author']:
						authorQuoteIndex.append(maxIndex)
				maxIndex = maxIndex - 1

			try:
				if int(page) < 1:
					embed.title = "Cannot search quotes"
					embed.description = "Invalid page. The page must be greater than one."
				else:
					authorDisplayName = quoteAuthor
					try:
						authorUser = await ctx.bot.fetch_user(int(quoteAuthor.lstrip("<@!").rstrip(">")))
						authorDisplayName = authorUser.display_name
						embed.set_thumbnail(url=(authorUser.avatar_url.BASE + authorUser.avatar_url._url))
					except (NotFound, ValueError):
						embed.set_footer(text="Cannot get the profile picture for this user, try using a mention")

					embed.title = "Searching Quotes by " + authorDisplayName

					# Check if we're on the first page
					if page == 1:
						if len(authorQuoteIndex) != 0:
							# List the first 5 quotes if the length of the index isn't zero
							embed.description += "Listing the first five quotes by this author: \n\n"
							iteration = 0
							# Iterate through the index and build a response
							for i in authorQuoteIndex:
								embed.description += data[authorQuoteIndex[iteration] - 1]["content"] + " **Quote #" + str(
									authorQuoteIndex[iteration] - 1) + "**\n"
								iteration = iteration + 1
								if iteration >= 5:
									break
						else:
							embed.description = "This author doesn't have any quotes."
					else:
						# Check if there are enough quotes to fill a page
						if len(authorQuoteIndex) <= 5 or len(authorQuoteIndex) <= ((page - 1) * 5):
							embed.description += "This author doesn't have enough quotes to reach this page. \n"
							embed.description += "They have **" + str(
								math.ceil(len(authorQuoteIndex) / 5)) + "** pages of quotes."
						else:
							# List the next 5 by page number
							embed.description += "Listing the next five quotes by this author (**Page " + str(page) + "**): \n\n"
							# Set the iteration by multiplying the page number by 5. First, shift left 1 (as indexes start at 0)
							iteration = (page - 1) * 5
							# Iterate through the index and build a response
							currentQuotesOnPage = 0
							remainingQuotes = len(authorQuoteIndex) - iteration
							while remainingQuotes > 0:
								embed.description += data[authorQuoteIndex[iteration] - 1]["content"] + " **Quote #" + str(
									authorQuoteIndex[iteration]) + "**\n"
								iteration = iteration + 1
								remainingQuotes = remainingQuotes - 1
								currentQuotesOnPage = currentQuotesOnPage + 1
								if currentQuotesOnPage >= 5:
									break

			except ValueError:
				embed.title = "Cannot search quotes"
				embed.description = "The page must be a number."

		await ctx.send(embed=embed)
