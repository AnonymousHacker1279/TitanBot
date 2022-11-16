import math
from datetime import datetime
from random import randint

import discord
from discord.errors import NotFound
from discord.ext import commands
from discord.ext.bridge import bot

from ..FileSystemAPI import DatabaseObjects
from ..FileSystemAPI.CacheManager.ListCacheManager import ListCacheManager
from ..GeneralUtilities import GeneralUtilities, PermissionHandler, QuoteUtils


class Quotes(commands.Cog):
	"""Remember the silly stuff people say."""

	def __init__(self, management_portal_handler):
		self.cache_managers = {}
		self.mph = management_portal_handler

	async def post_initialize(self, bot: commands.Bot):
		for guild in bot.guilds:
			self.cache_managers[guild.id] = ListCacheManager("quotes", guild.id,
															await DatabaseObjects.get_quotes_database(guild.id),
															management_portal_handler=self.mph)

	# When the bot joins a new guild, caches need to be invalidated
	async def invalidate_caches(self):
		for guild in self.cache_managers:
			await self.cache_managers[guild].sync_cache_to_disk()
			await self.cache_managers[guild].invalidate_cache()

	@bot.bridge_command(aliases=["q"])
	@commands.guild_only()
	async def quote(self, ctx: discord.ApplicationContext, quote_id=None):
		"""Get a random quote, if an ID isn't provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "quote")
		if not failedPermissionCheck:

			# Check if an ID is provided, if not get a random quote
			data = await self.cache_managers.get(ctx.guild.id).get_cache()
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

				embed = await QuoteUtils.prepare_quote(ctx, embed, author, content, str(random), date, quoted_by)

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
						embed = await QuoteUtils.prepare_quote(ctx, embed, author, content, quote_id, date, quoted_by)
				except ValueError:
					embed.title = "Cannot get quote"
					embed.description = "The quote ID must be a number."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "quote", ctx.guild.id)

	@bot.bridge_command(aliases=["tq"])
	@commands.guild_only()
	async def total_quotes(self, ctx: discord.ApplicationContext):
		"""Get the total number of quotes available."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "total_quotes")
		if not failedPermissionCheck:
			data = await self.cache_managers.get(ctx.guild.id).get_cache()

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
		await self.mph.update_management_portal_command_used("quotes", "total_quotes", ctx.guild.id)

	@bot.bridge_command(aliases=["aq"])
	@commands.guild_only()
	async def add_quote(self, ctx: discord.ApplicationContext, quote: str, author: str):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "add_quote")
		if not failedPermissionCheck:
			cache_manager = self.cache_managers.get(ctx.guild.id)
			data = await cache_manager.get_cache()

			try:
				author = int(await GeneralUtilities.strip_usernames(author))
			except ValueError:
				pass

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
		await self.mph.update_management_portal_command_used("quotes", "add_quote", ctx.guild.id)

	@commands.message_command(name='Add Quote')
	@commands.guild_only()
	async def add_quote_message_cmd(self, ctx: discord.ApplicationContext, message: discord.Message):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "add_quote")
		if not failedPermissionCheck:
			cache_manager = self.cache_managers.get(ctx.guild.id)
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
		await self.mph.update_management_portal_command_used("quotes", "add_quote", ctx.guild.id)

	@bot.bridge_command(aliases=["rq"])
	@commands.guild_only()
	async def remove_quote(self, ctx: discord.ApplicationContext, quote_id: int):
		"""Need to purge a quote? Use this. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "remove_quote", True)
		if not failedPermissionCheck:

			cache_manager = self.cache_managers.get(ctx.guild.id)
			data = await cache_manager.get_cache()

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			if quote_id < 0 or quote_id > maxIndex:
				embed.title = "Failed to remove quote"
				embed.description = "You must pass a quote ID to remove."
			else:
				await cache_manager.remove_from_list_cache(data[quote_id])
				await cache_manager.sync_cache_to_disk()

			embed.title = "Quote Removed"
			embed.description = "The quote has been purged from my archives. Total Quotes: **" + str(
				maxIndex - 1) + ".**"

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "remove_quote", ctx.guild.id)

	@bot.bridge_command(aliases=["eq"])
	@commands.guild_only()
	async def edit_quote(self, ctx: discord.ApplicationContext, quote_id: int, quote: str = "", author: str = ""):
		"""Need to edit a quote? Use this. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "edit_quote", True)
		if not failedPermissionCheck:

			cache_manager = self.cache_managers.get(ctx.guild.id)
			data = await cache_manager.get_cache()

			maxIndex = 0
			for _ in data:
				maxIndex = maxIndex + 1
			maxIndex = maxIndex - 1

			if quote_id < 0 or quote_id > maxIndex:
				embed.title = "Failed to edit quote"
				embed.description = "You must pass a valid quote ID to edit. It must be greater than 0 and less" \
									" than the total number of quotes."
			elif quote == "" and author == "":
				embed.title = "Failed to edit quote"
				embed.description = "You must pass a quote and/or author to edit."
			else:
				# Get the quote data
				quote_data = data[quote_id]
				# If the content is not empty, update it
				if quote != "":
					quote_data["content"] = quote
				# If the author is not empty, modify the author
				if author != "":
					try:
						author = int(await GeneralUtilities.strip_usernames(author))
					except ValueError:
						pass
					quote_data["author"] = author

				await cache_manager.edit_list_cache(data[quote_id], quote_data)
				await cache_manager.sync_cache_to_disk()

			embed.title = "Quote Edited"
			embed.description = "The quote has been edited in my archives."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "edit_quote", ctx.guild.id)

	@bot.bridge_command(aliases=["sqa"])
	@commands.guild_only()
	async def search_quotes_author(self, ctx: discord.ApplicationContext, quote_author: str, page: int = 0):
		"""Search quotes by author. Lists up to 10 per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "search_quotes_author")
		if not failedPermissionCheck:
			quote_author = await GeneralUtilities.strip_usernames(quote_author)

			# Get the quote data
			data = await self.cache_managers.get(ctx.guild.id).get_cache()

			maxIndex = 0
			# The quote index here lists all quote IDs associated with the author
			authorQuoteIndex = []
			for i in data:
				if quote_author in str(i['author']):
					authorQuoteIndex.append(maxIndex)
				maxIndex = maxIndex + 1

			if page < 0:
				embed.title = "Cannot search quotes"
				embed.description = "Invalid page. The page must be greater than zero."
			else:
				authorDisplayName = quote_author

				# Try getting a profile picture for the author and a display name
				try:
					authorUser = await ctx.bot.fetch_user(int(quote_author))
					authorDisplayName = authorUser.display_name
					embed.set_thumbnail(url=authorUser.display_avatar.url)
				except (NotFound, ValueError):
					embed.set_footer(text="Cannot get the profile picture for this user, try using a mention")

				embed.title = "Searching Quotes by " + authorDisplayName

				# Check if we're on the first page
				if page == 0:
					if len(authorQuoteIndex) != 0:
						# List the first 10 quotes if the length of the index isn't zero
						embed.description += "Listing the first ten quotes by this author: \n\n"
						iteration = 0
						# Iterate through the index and build a response
						for _ in authorQuoteIndex:
							embed.description += data[authorQuoteIndex[iteration]]["content"] + " **Quote #" + str(
								authorQuoteIndex[iteration]) + "**\n"
							iteration = iteration + 1
							if iteration >= 10:
								break
					else:
						embed.description = "This author doesn't have any quotes."
				else:
					# Check if there are enough quotes to fill a page
					if len(authorQuoteIndex) <= 10 or len(authorQuoteIndex) <= (page * 10):
						embed.description += "This author doesn't have enough quotes to reach this page. \n"
						embed.description += "They have **" + str(
							math.ceil(len(authorQuoteIndex) / 10)) + "** pages of quotes."
					else:
						# List the next 10 by page number
						embed.description += "Listing the next ten quotes by this author (**Page " + str(page) + "**): \n\n"
						# Set the iteration by multiplying the page number by 0. First, shift left 1 (as indexes start at 0)
						iteration = page * 10
						# Iterate through the index and build a response
						currentQuotesOnPage = 0
						remainingQuotes = len(authorQuoteIndex) - iteration
						while remainingQuotes > 0:
							embed.description += data[authorQuoteIndex[iteration]]["content"] + " **Quote #" + str(
								authorQuoteIndex[iteration]) + "**\n"
							iteration = iteration + 1
							remainingQuotes = remainingQuotes - 1
							currentQuotesOnPage = currentQuotesOnPage + 1
							if currentQuotesOnPage >= 10:
								break

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "search_quotes_author", ctx.guild.id)

	@bot.bridge_command(aliases=["sqt"])
	@commands.guild_only()
	async def search_quotes_text(self, ctx: discord.ApplicationContext, text: str, page: int = 0):
		"""Search quotes by text. Lists up to 10 per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "search_quotes_text")
		if not failedPermissionCheck:
			# Get the quote data
			data = await self.cache_managers.get(ctx.guild.id).get_cache()

			maxIndex = 0
			# The quote index here lists all quote IDs associated with the author
			quoteIndex = []
			for i in data:
				if text.lower() in str(i['content']).lower():
					quoteIndex.append(maxIndex)
				maxIndex = maxIndex + 1

			embed.title = "Searching Quotes containing '" + text + "'"

			# Check if we're on the first page
			if page == 0:
				if len(quoteIndex) != 0:
					# List the first 10 quotes if the length of the index isn't zero
					embed.description += "Listing the first ten quotes found: \n\n"
					iteration = 0
					# Iterate through the index and build a response
					for _ in quoteIndex:
						embed.description += data[quoteIndex[iteration]]["content"] + " **Quote #" + str(
								quoteIndex[iteration]) + "**\n"
						iteration = iteration + 1
						if iteration >= 10:
							break
				else:
					embed.description = "No quotes were found with the text provided."
			else:
				# Check if there are enough quotes to fill a page
				if len(quoteIndex) <= 10 or len(quoteIndex) <= (page * 10):
					embed.description += "There aren't enough quotes to reach this page. \n"
					embed.description += "They have **" + str(
							math.ceil(len(quoteIndex) / 10)) + "** pages of quotes."
				else:
					# List the next 10 by page number
					embed.description += "Listing the next ten quotes found (**Page " + str(page) + "**): \n\n"
					# Set the iteration by multiplying the page number by 0. First, shift left 1 (as indexes start at 0)
					iteration = page * 10
					# Iterate through the index and build a response
					currentQuotesOnPage = 0
					remainingQuotes = len(quoteIndex) - iteration
					while remainingQuotes > 0:
						embed.description += data[quoteIndex[iteration]]["content"] + " **Quote #" + str(
								quoteIndex[iteration]) + "**\n"
						iteration = iteration + 1
						remainingQuotes = remainingQuotes - 1
						currentQuotesOnPage = currentQuotesOnPage + 1
						if currentQuotesOnPage >= 10:
							break

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "search_quotes_text", ctx.guild.id)

	@bot.bridge_command(aliases=["lrq"])
	@commands.guild_only()
	async def list_recent_quotes(self, ctx: discord.ApplicationContext):
		"""Listing ten of the most recent quotes"""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "quotes", "list_recent_quotes")
		if not failedPermissionCheck:

			# Get the quote data
			data = await self.cache_managers.get(ctx.guild.id).get_cache()

			maxIndex = 0
			# Quote index for 10 newest quotes
			quoteIndex = []
			for i in data:

				if len(quoteIndex) != 0:

					# List the first 10 quotes if the length of the index isn't zero
					embed.description += "Listing ten of the most recent quotes: \n\n"
					iteration = 0
					# Iterate through the index and build a response
					for _ in quoteIndex:
						embed.description += data[quoteIndex[iteration]]["content"] + " **Quote #" + str(
						quoteIndex[iteration]) + "**\n" + ["author"]
						iteration = iteration + 1
						if iteration >= 10:
							break
					else:
						embed.title = "Failed to List Recent Quotes"
						embed.description = "I do not have any quotes in my archives."
							break

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "list_recent_quotes", ctx.guild.id)
