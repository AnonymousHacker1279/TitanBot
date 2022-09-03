import math
import re
from datetime import datetime
from random import randint

import discord
from discord.errors import NotFound
from discord.ext import commands

from ..FileSystemAPI import DatabaseObjects
from ..FileSystemAPI.CacheManager.ListCacheManager import ListCacheManager
from ..GeneralUtilities import GeneralUtilities, PermissionHandler


class Quotes(commands.Cog):
	"""Remember the silly stuff people say."""

	def __init__(self):
		self.cache_managers = {}

	async def post_initialize(self, bot: commands.Bot):
		for guild in bot.guilds:
			self.cache_managers[guild.id] = ListCacheManager(await DatabaseObjects.get_quotes_database(guild.id))

	@commands.slash_command(name='quote')
	@commands.guild_only()
	async def quote(self, ctx: discord.ApplicationContext, quote_id=None):
		"""Get a random quote, if an ID isn't provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "quote")
		if not failedPermissionCheck:

			async def prepare_quote(pAuthor, pContent, pId, pDate, pQuotedBy) -> discord.Embed:
				embed.title = "Quote #" + pId

				links = re.findall('https://[a-zA-Z0-9-./_&]*', pContent)
				contentExcludingLinks = ""
				iteration = 0

				if pDate and pQuotedBy != "Unknown":
					iso_date = datetime.fromisoformat(pDate)
					readable_date = str(iso_date.month) + "/" + str(iso_date.day) + "/" + str(iso_date.year) \
									+ " at " + str(iso_date.hour) + \
									":" + str(iso_date.minute) + ":" + str(iso_date.second)
				else:
					readable_date = "Unknown"
					pQuotedBy = "Unknown"

				for _ in links:
					contentExcludingLinks = re.sub(pattern=links[iteration], repl="", string=pContent)
					iteration += 1
				if len(links) != 0:
					if contentExcludingLinks == "":
						embed.set_image(url=links[0])
						embed.description = pAuthor
						embed.set_footer(text="Added " + readable_date + " by " + str(await ctx.bot.fetch_user(pQuotedBy)))
					else:
						embed.description = '> "' + pContent + '"\n'
						embed.description += " - <@" + str(pAuthor) + ">"
						embed.set_image(url=links[0])
						embed.set_footer(text="Added " + str(readable_date) + " by " + str(await ctx.bot.fetch_user(pQuotedBy)))
				else:
					embed.description = '> "' + pContent + '"\n'
					embed.description += " - <@" + str(pAuthor) + ">"
					embed.set_footer(text="Added " + str(readable_date) + " by " + str(await ctx.bot.fetch_user(pQuotedBy)))

				try:
					authorUser = await ctx.bot.fetch_user(pAuthor)
					embed.set_thumbnail(url=authorUser.display_avatar.url)
				except (NotFound, ValueError):
					embed.set_footer(text="Cannot get the profile picture for this user, try using a mention")

				return embed

			# Check if an ID is provided, if not get a random quote
			data = await self.cache_managers.get(ctx.guild_id).get_cache()
			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			if maxIndex == -1:
				embed.title = "Failed to Get Quote"
				embed.description = "I do not have any quotes in my archives."
			elif quote_id is None:
				random = randint(0, maxIndex)
				author = data[random]["author"]
				content = data[random]["content"]
				date = data[random]["date"]
				quoted_by = data[random]["quoted_by"]

				embed = await prepare_quote(author, content, str(random), date, quoted_by)

			else:
				try:
					if int(quote_id) < 0 or int(quote_id) > maxIndex:
						embed.title = "Cannot get quote"
						embed.description = "Invalid quote ID. It must not be less than zero and must be less than the " \
							"total number of quotes. "
					else:
						content = data[int(quote_id)]["content"]
						author = data[int(quote_id)]["author"]
						date = data[int(quote_id)]["date"]
						quoted_by = data[int(quote_id)]["quoted_by"]
						embed = await prepare_quote(author, content, quote_id, date, quoted_by)
				except ValueError:
					embed.title = "Cannot get quote"
					embed.description = "The quote ID must be a number."

		await ctx.respond(embed=embed)

	@commands.slash_command(name='total_quotes')
	@commands.guild_only()
	async def total_quotes(self, ctx: discord.ApplicationContext):
		"""Get the total number of quotes available."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "total_quotes")
		if not failedPermissionCheck:
			data = await self.cache_managers.get(ctx.guild_id).get_cache()

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
		await ctx.respond(embed=embed)

	@commands.slash_command(name='add_quote')
	@commands.guild_only()
	async def add_quote(self, ctx: discord.ApplicationContext, quote: str, author: str):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "add_quote")
		if not failedPermissionCheck:
			cache_manager = self.cache_managers.get(ctx.guild_id)
			data = await cache_manager.get_cache()

			author = int(await GeneralUtilities.strip_usernames(author))

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			await cache_manager.add_to_list_cache({"content": quote, "author": author,
												"date": datetime.now().isoformat(), "quoted_by": ctx.author.id})
			await cache_manager.sync_cache_to_disk()

			embed.title = "Quote Added"
			embed.description = "The quote has been added to my archives as **Quote #" + str(maxIndex + 1) + ".**"
		await ctx.respond(embed=embed)

	@commands.message_command(name='Add Quote')
	@commands.guild_only()
	async def add_quote_message_cmd(self, ctx: discord.ApplicationContext, message: discord.Message):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "add_quote")
		if not failedPermissionCheck:
			cache_manager = self.cache_managers.get(ctx.guild_id)
			data = await cache_manager.get_cache()

			author = message.author.id

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			await cache_manager.add_to_list_cache({"content": message.content, "author": author,
												"date": datetime.now().isoformat(), "quoted_by": ctx.author.id})
			await cache_manager.sync_cache_to_disk()

			embed.title = "Quote Added"
			embed.description = "The quote has been added to my archives as **Quote #" + str(maxIndex + 1) + ".**"
		await ctx.respond(embed=embed)

	@commands.slash_command(name='remove_quote')
	@commands.guild_only()
	async def remove_quote(self, ctx: discord.ApplicationContext, quote_id=None):
		"""Need to purge a quote? Use this. Only available to TitanBot Wizards."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "remove_quote", True)
		if not failedPermissionCheck:
			if quote_id is None:
				embed.title = "Failed to remove quote"
				embed.description = "You must pass a quote ID to remove."

			cache_manager = self.cache_managers.get(ctx.guild_id)
			data = await cache_manager.get_cache()

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			try:
				if int(quote_id) < 0 or int(quote_id) > maxIndex:
					embed.title = "Failed to remove quote"
					embed.description = "You must pass a quote ID to remove."
				else:
					await cache_manager.remove_from_list_cache(data[int(quote_id)])
					await cache_manager.sync_cache_to_disk()

				embed.title = "Quote Removed"
				embed.description = "The quote has been purged from my archives. Total Quotes: **" + str(
					maxIndex - 1) + ".**"
			except ValueError:
				embed.title = "Failed to remove quote"
				embed.description = "The quote ID must be a number."

		await ctx.respond(embed=embed)

	@commands.slash_command(name='search_quotes')
	@commands.guild_only()
	async def search_quotes(self, ctx: discord.ApplicationContext, quote_author: str = None, page: int = 1):
		"""Search quotes by author. Lists up to 5 per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "search_quotes")
		if not failedPermissionCheck:
			# Check if an author was provided
			if quote_author is None:
				embed.title = "Cannot search quotes"
				embed.description = "You must provide an author"

			quote_author = await GeneralUtilities.strip_usernames(quote_author)

			# Get the quote data
			data = await self.cache_managers.get(ctx.guild_id).get_cache()

			maxIndex = 0
			# The quote index here lists all quote IDs associated with the author
			authorQuoteIndex = []
			for i in data:
				maxIndex = maxIndex + 1
				if quote_author in str(i['author']):
					authorQuoteIndex.append(maxIndex)

			try:
				if int(page) < 1:
					embed.title = "Cannot search quotes"
					embed.description = "Invalid page. The page must be greater than one."
				else:
					authorDisplayName = quote_author
					try:
						authorUser = await ctx.bot.fetch_user(int(quote_author))
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

		await ctx.respond(embed=embed)
