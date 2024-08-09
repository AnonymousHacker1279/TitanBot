import math
from datetime import datetime

import discord
from discord import default_permissions
from discord.ext import commands

from Framework.CommandGroups.BasicCog import BasicCog
from Framework.CommandGroups.Views.SearchQuotesView import SearchQuotesView, SearchTypes
from Framework.GeneralUtilities import PermissionHandler, QuoteUtils


class Quotes(BasicCog):
	"""Remember the silly stuff people say."""

	quotes = discord.SlashCommandGroup("quotes", description="Remember the silly stuff people say.")

	@quotes.command()
	@discord.option(
		name="quote_id",
		description="The ID of a quote to get.",
		type=int,
		required=False
	)
	@commands.guild_only()
	async def quote(self, ctx: discord.ApplicationContext, quote_id: int = None):
		"""Get a random quote, if an ID isn't provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:
			# Check if a quote ID was provided
			if quote_id is None:
				# Get a random quote
				response = await self.sql_bridge.quotes_module.get_quote(ctx.guild.id)
			else:
				# Get the quote with the provided ID
				response = await self.sql_bridge.quotes_module.get_quote(ctx.guild.id, quote_id)

			# Check if the response is empty
			if len(response) == 0:
				embed.title = "Failed to Get Quote"
				embed.description = "You either provided an invalid quote ID, or there are no quotes in the database."

			else:
				content = response[1]
				author = response[2]
				date = response[4]
				quoted_by = response[3]
				quote_number = response[0]
				embed = await QuoteUtils.prepare_quote(ctx, embed, author, content, quote_number, date, quoted_by)

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("quotes", "quote", ctx.guild.id)

	@quotes.command()
	@discord.option(
		name="get_global_count",
		description="Get the total number of quotes across all guilds.",
		type=bool,
		required=False
	)
	@commands.guild_only()
	async def total(self, ctx: discord.ApplicationContext, get_global_count: bool = False):
		"""Get the total number of quotes available."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:
			count = await self.sql_bridge.quotes_module.get_total_quotes(ctx.guild.id, get_global_count)

			embed.title = "Total Quotes"
			if count == 0:
				embed.description = "I have do not have any quotes in my archives."
			else:
				if get_global_count:
					embed.description = "I have " + str(count) + " quotes in my archives across all guilds."
				else:
					embed.description = "I have " + str(count) + " quotes in my archives for this guild."

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("quotes", "total", ctx.guild.id)

	@quotes.command()
	@discord.option(
		name="quote",
		description="The quote to add.",
		type=str,
		required=True
	)
	@discord.option(
		name="author",
		description="The author of the quote.",
		type=discord.User,
		required=True
	)
	@commands.guild_only()
	async def add(self, ctx: discord.ApplicationContext, quote: str, author: discord.User):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:
			quote_number = await self.sql_bridge.quotes_module.add_quote(ctx.guild.id, quote, author.id, ctx.author.id)

			# Display the quote being added
			current_date = str(datetime.now())
			embed = await QuoteUtils.prepare_quote(ctx, embed, author.id, quote, quote_number, current_date, ctx.author.id)

			embed.title = "Quote Added: #" + str(quote_number)

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("quotes", "add", ctx.guild.id)

	@commands.message_command(name='Add Quote')
	@commands.guild_only()
	async def add_message_cmd(self, ctx: discord.ApplicationContext, message: discord.Message):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:
			quote_number = await self.sql_bridge.quotes_module.add_quote(ctx.guild.id, message.content, message.author.id, ctx.author.id)

			# Display the quote being added
			current_date = str(datetime.now())
			embed = await QuoteUtils.prepare_quote(ctx, embed, message.author.id, message.content, quote_number, current_date, ctx.author.id)

			embed.title = "Quote Added: #" + str(quote_number)

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("quotes", "add", ctx.guild.id)

	@quotes.command()
	@discord.option(
		name="quote_id",
		description="The ID of a quote to remove.",
		type=int,
		required=True
	)
	@commands.guild_only()
	@default_permissions(administrator=True)
	async def remove(self, ctx: discord.ApplicationContext, quote_id: int):
		"""Need to purge a quote? Use this."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:

			if quote_id < 0:
				embed.title = "Failed to remove quote"
				embed.description = "You cannot remove a quote with a negative ID."
			else:
				# Check if the response is empty
				if await self.sql_bridge.quotes_module.remove_quote(ctx.guild.id, quote_id):
					embed.title = "Quote Removed"
					embed.description = "The quote has been removed from my archives."
				else:
					embed.title = "Failed to remove quote"
					embed.description = "You either provided an invalid quote ID (out of bounds), or there are no quotes in the database."

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("quotes", "remove", ctx.guild.id)

	@quotes.command()
	@discord.option(
		name="quote_id",
		description="The ID of a quote to edit.",
		type=int,
		required=True
	)
	@discord.option(
		name="quote",
		description="A new quote to replace the old one.",
		type=str,
		required=False
	)
	@discord.option(
		name="author",
		description="A new author to replace the old one.",
		type=discord.User,
		required=False
	)
	@commands.guild_only()
	@default_permissions(administrator=True)
	async def edit(self, ctx: discord.ApplicationContext, quote_id: int, quote: str = None, author: discord.User = None):
		"""Need to edit a quote? Use this. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:

			if quote_id < 0:
				embed.title = "Failed to edit quote"
				embed.description = "You must pass a valid quote ID to edit. It must be greater than 0 and less" \
									" than the total number of quotes."
			elif quote is None and author is None:
				embed.title = "Failed to edit quote"
				embed.description = "You must pass a quote and/or author to edit."
			else:
				if await self.sql_bridge.quotes_module.edit_quote(ctx.guild.id, quote_id, quote, author):
					embed.title = "Quote Edited"
					embed.description = "The quote has been edited in my archives."
				else:
					embed.title = "Failed to edit quote"
					embed.description = "You either provided an invalid quote ID, or there are no quotes in the database."

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("quotes", "edit", ctx.guild.id)

	@quotes.command()
	@discord.option(
		name="quote_author",
		description="An author to search for quotes by.",
		type=discord.User,
		required=True
	)
	@discord.option(
		name="page",
		description="The page of quotes to display. This is zero-indexed, so the first page is 0.",
		type=int,
		required=False
	)
	@discord.option(
		name="descending_order",
		description="Sort the quotes in descending order.",
		type=bool,
		required=False
	)
	@commands.guild_only()
	async def search_author(self, ctx: discord.ApplicationContext, quote_author: discord.User, page: int = 0, descending_order: bool = False):
		"""Search quotes by author. Lists up to ten per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		total_quotes = 0

		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:
			embed, total_quotes = await QuoteUtils.handle_searching_author(ctx, self.sql_bridge, page, embed, quote_author.id, descending_order)

		view = SearchQuotesView(ctx, self.sql_bridge, page, total_quotes, SearchTypes.AUTHOR, quote_author.id, None, descending_order)

		if page <= 0:
			view.previous_page.disabled = True
		if page >= math.ceil(total_quotes / 10) - 1:
			view.next_page.disabled = True

		await ctx.respond(embed=embed, view=view)
		await self.update_usage_analytics("quotes", "search_author", ctx.guild.id)

	@discord.option(
		name="text",
		description="A snippet of text to search for.",
		type=str,
		required=True
	)
	@discord.option(
		name="page",
		description="The page of quotes to display. This is zero-indexed, so the first page is 0.",
		type=int,
		required=False
	)
	@discord.option(
		name="descending_order",
		description="Sort the quotes in descending order.",
		type=bool,
		required=False
	)
	@quotes.command()
	@commands.guild_only()
	async def search_text(self, ctx: discord.ApplicationContext, text: str, page: int = 0, descending_order: bool = False):
		"""Search quotes by text. Lists up to ten per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		total_quotes = 0

		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:
			embed, total_quotes = await QuoteUtils.handle_searching_content(ctx, self.sql_bridge, page, embed, text, descending_order)

		view = SearchQuotesView(ctx, self.sql_bridge, page, total_quotes, SearchTypes.CONTENT, None, text, descending_order)

		if page <= 0:
			view.previous_page.disabled = True
		if page >= math.ceil(total_quotes / 10) - 1:
			view.next_page.disabled = True

		await ctx.respond(embed=embed, view=view)
		await self.update_usage_analytics("quotes", "search_text", ctx.guild.id)

	@quotes.command()
	@commands.guild_only()
	async def list_recent(self, ctx: discord.ApplicationContext):
		"""List ten of the most recent quotes"""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "quotes")
		if not failed_permission_check:

			# Get the quotes
			quotes = await self.sql_bridge.quotes_module.list_recent(ctx.guild.id)

			# Check if the response is empty
			if len(quotes) == 0:
				embed.title = "No Quotes Found"
				embed.description = "No quotes have been added yet."
			else:
				embed.title = "Recent Quotes"

				# Add the quotes to the embed
				for quote in quotes:
					embed.add_field(name="Quote #" + str(quote[0]), value=quote[1])

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("quotes", "list_recent", ctx.guild.id)
