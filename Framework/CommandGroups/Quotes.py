import json
import math
import re
from random import randint

import discord
from discord.errors import NotFound
from discord.ext import commands

from ..GeneralUtilities import GeneralUtilities as Utilities, PermissionHandler


class Quotes(commands.Cog):
	"""Remember the silly stuff people say."""

	@commands.command(name='quote', aliases=["q"])
	@commands.guild_only()
	async def quote(self, ctx, quoteID=None):
		"""Get a random quote, if an ID isn't provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "quote")
		if not failedPermissionCheck:

			async def prepare_quote(pAuthor, pContent, pId):
				embed.title = "Quote #" + pId

				links = re.findall('https://[a-zA-Z0-9-./_]*', pContent)
				contentExcludingLinks = ""
				iteration = 0
				for _ in links:
					contentExcludingLinks = re.sub(pattern=links[iteration], repl="", string=pContent)
					iteration += 1
				if len(links) != 0:
					if contentExcludingLinks == "":
						embed.set_image(url=links[0])
						embed.description = pAuthor
					else:
						embed.description = '> "' + pContent + '"\n'
						embed.description += " - " + pAuthor
						embed.set_image(url=links[0])
				else:
					embed.description = '> "' + pContent + '"\n'
					embed.description += " - " + pAuthor

				try:
					authorUser = await ctx.bot.fetch_user(int(pAuthor.lstrip("<@!").rstrip(">")))
					embed.set_thumbnail(url=authorUser.display_avatar.url)
				except (NotFound, ValueError):
					embed.set_footer(text="Cannot get the profile picture for this user, try using a mention")

				return embed

			# Check if an ID is provided, if not get a random quote
			with open(await Utilities.get_quotes_database(), 'r') as f:
				data = json.load(f)

				maxIndex = 0
				for _ in data:
					maxIndex = maxIndex + 1
				maxIndex = maxIndex - 1
			if maxIndex == -1:
				embed.title = "Failed to Get Quote"
				embed.description = "I do not have any quotes in my archives."
			elif quoteID is None:
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

	@commands.command(name='totalQuotes', aliases=["tq"])
	@commands.guild_only()
	async def total_quotes(self, ctx):
		"""Get the total number of quotes available."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "totalQuotes")
		if not failedPermissionCheck:
			with open(await Utilities.get_quotes_database(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			embed.title = "Total Quotes"
			if maxIndex == -1:
				embed.description = "I have do not have any quotes in my archives."
			else:
				embed.description = "I have " + str(maxIndex) + " quotes in my archives."
			embed.set_footer(text="Note, this is zero-indexed and counting starts at zero, not one.")
		await ctx.send(embed=embed)

	@commands.command(name='addQuote', aliases=["aq"])
	@commands.guild_only()
	async def add_quote(self, ctx, quote: str, author: str):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "addQuote")
		if not failedPermissionCheck:
			with open(await Utilities.get_quotes_database(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			with open(await Utilities.get_quotes_database(), 'w') as f:
				quoteDictionary = {"content": quote, "author": author}
				data.append(quoteDictionary)
				json.dump(data, f, indent=4)

			embed.title = "Quote Added"
			embed.description = "The quote has been added to my archives as **Quote #" + str(maxIndex + 1) + ".**"
		await ctx.send(embed=embed)

	@commands.command(name='removeQuote', aliases=["rq"])
	@commands.guild_only()
	async def remove_quote(self, ctx, quoteID=None):
		"""Need to purge a quote? Use this. Only available to TitanBot Wizards."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "removeQuote", True)
		if not failedPermissionCheck:
			if quoteID is None:
				embed.title = "Failed to remove quote"
				embed.description = "You must pass a quote ID to remove."

			with open(await Utilities.get_quotes_database(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			try:
				if int(quoteID) < 0 or int(quoteID) > maxIndex:
					embed.title = "Failed to remove quote"
					embed.description = "You must pass a quote ID to remove."
				else:
					with open(await Utilities.get_quotes_database(), 'w') as f:
						data.remove(data[int(quoteID)])
						json.dump(data, f, indent=4)

				embed.title = "Quote Removed"
				embed.description = "The quote has been purged from my archives. Total Quotes: **" + str(
					maxIndex - 1) + ".**"
			except ValueError:
				embed.title = "Failed to remove quote"
				embed.description = "The quote ID must be a number."

		await ctx.send(embed=embed)

	@commands.command(name='searchQuotes', aliases=["sq"])
	@commands.guild_only()
	async def search_quotes(self, ctx, quoteAuthor=None, page=1):
		"""Search quotes by author. Lists up to 5 per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "searchQuotes")
		if not failedPermissionCheck:
			# Check if an author was provided
			if quoteAuthor is None:
				embed.title = "Cannot search quotes"
				embed.description = "You must provide an author"
			quoteAuthor = str(quoteAuthor)

			# Get the quote data
			with open(await Utilities.get_quotes_database(), 'r') as f:
				data = json.load(f)

				maxIndex = 0
				# The quote index here lists all quote IDs associated with the author
				authorQuoteIndex = []
				for i in data:
					maxIndex = maxIndex + 1
					if quoteAuthor in i['author']:
						authorQuoteIndex.append(maxIndex)

			try:
				if int(page) < 1:
					embed.title = "Cannot search quotes"
					embed.description = "Invalid page. The page must be greater than one."
				else:
					authorDisplayName = quoteAuthor
					try:
						authorUser = await ctx.bot.fetch_user(int(quoteAuthor.lstrip("<@!").rstrip(">")))
						authorDisplayName = authorUser.display_name
						embed.set_thumbnail(url=authorUser.display_avatar.url)
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
							for _ in authorQuoteIndex:
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
									authorQuoteIndex[iteration] - 1) + "**\n"
								iteration = iteration + 1
								remainingQuotes = remainingQuotes - 1
								currentQuotesOnPage = currentQuotesOnPage + 1
								if currentQuotesOnPage >= 5:
									break

			except ValueError:
				embed.title = "Cannot search quotes"
				embed.description = "The page must be a number."

		await ctx.send(embed=embed)
