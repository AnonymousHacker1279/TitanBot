import math

import discord
from discord.ext import commands

from .Views.SearchQuotesView import SearchQuotesView, SearchTypes
from ..GeneralUtilities import PermissionHandler, QuoteUtils
from ..ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


class Quotes(commands.Cog):
	"""Remember the silly stuff people say."""

	quotes = discord.SlashCommandGroup("quotes", description="Remember the silly stuff people say.")

	def __init__(self, management_portal_handler: ManagementPortalHandler):
		self.mph = management_portal_handler

	@quotes.command()
	@commands.guild_only()
	async def quote(self, ctx: discord.ApplicationContext, quote_id: int = None):
		"""Get a random quote, if an ID isn't provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "quote")
		if not failedPermissionCheck:

			# Check if a quote ID was provided
			if quote_id is None:
				# Get a random quote
				quote_json = await self.mph.quotes.get_quote(ctx.guild.id, -1)
			else:
				# Get the quote with the provided ID
				quote_json = await self.mph.quotes.get_quote(ctx.guild.id, quote_id)

			# Check if the response is empty
			if len(quote_json) == 0:
				embed.title = "Failed to Get Quote"
				embed.description = "You either provided an invalid quote ID, or there are no quotes in the database."

			else:
				content = quote_json["content"]
				author = quote_json["author"]
				date = quote_json["date"]
				quoted_by = quote_json["quoted_by"]
				quote_number = str(quote_json["quote_number"])
				embed = await QuoteUtils.prepare_quote(ctx, embed, author, content, quote_number, date, quoted_by)

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "quote", ctx.guild.id)

	@quotes.command()
	@commands.guild_only()
	async def total_quotes(self, ctx: discord.ApplicationContext):
		"""Get the total number of quotes available."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "total_quotes")
		if not failedPermissionCheck:
			response = await self.mph.quotes.get_total_quotes(ctx.guild.id)
			total_quotes = response["total_quotes"]

			embed.title = "Total Quotes"
			if total_quotes == 0:
				embed.description = "I have do not have any quotes in my archives."
			else:
				embed.description = "I have " + str(total_quotes) + " quotes in my archives."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "total_quotes", ctx.guild.id)

	@quotes.command()
	@commands.guild_only()
	async def add_quote(self, ctx: discord.ApplicationContext, quote: str, author: discord.User):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "add_quote")
		if not failedPermissionCheck:
			response = await self.mph.quotes.add_quote(ctx.guild.id, quote, author.id, ctx.author.id)
			quote_number = response["quote_number"]

			embed.title = "Quote Added"
			embed.description = "The quote has been added to my archives as **Quote #" + str(quote_number) + ".**"

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "add_quote", ctx.guild.id)

	@commands.message_command(name='Add Quote')
	@commands.guild_only()
	async def add_quote_message_cmd(self, ctx: discord.ApplicationContext, message: discord.Message):
		"""Did someone say something stupid? Make them remember it with a quote."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "add_quote")
		if not failedPermissionCheck:
			response = await self.mph.quotes.add_quote(ctx.guild.id, message.content, message.author.id, ctx.author.id)
			quote_number = response["quote_number"]

			embed.title = "Quote Added"
			embed.description = "The quote has been added to my archives as **Quote #" + str(quote_number) + ".**"

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "add_quote", ctx.guild.id)

	@quotes.command()
	@commands.guild_only()
	async def remove_quote(self, ctx: discord.ApplicationContext, quote_id: int):
		"""Need to purge a quote? Use this. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "remove_quote", True)
		if not failedPermissionCheck:

			if quote_id < 0:
				embed.title = "Failed to remove quote"
				embed.description = "You cannot remove a quote with a negative ID."
			else:
				# Remove the quote with the provided ID
				response = await self.mph.quotes.remove_quote(ctx.guild.id, quote_id)
				remaining_quotes = response["quote_count"]

				# Check if the response is empty
				if len(response) == 0:
					embed.title = "Failed to remove quote"
					embed.description = "You either provided an invalid quote ID (out of bounds), or there are no quotes in the database."
				else:
					embed.title = "Quote Removed"
					embed.description = "The quote has been removed from my archives. There are now **" + str(remaining_quotes) + "** quotes in my archives."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "remove_quote", ctx.guild.id)

	@quotes.command()
	@commands.guild_only()
	async def edit_quote(self, ctx: discord.ApplicationContext, quote_id: int, quote: str = "", author: discord.User = None):
		"""Need to edit a quote? Use this. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "edit_quote", True)
		if not failedPermissionCheck:

			if quote_id < 0:
				embed.title = "Failed to edit quote"
				embed.description = "You must pass a valid quote ID to edit. It must be greater than 0 and less" \
									" than the total number of quotes."
			elif quote == "" and author is None:
				embed.title = "Failed to edit quote"
				embed.description = "You must pass a quote and/or author to edit."
			else:
				await self.mph.quotes.edit_quote(ctx.guild.id, quote_id, quote, author)

				embed.title = "Quote Edited"
				embed.description = "The quote has been edited in my archives."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "edit_quote", ctx.guild.id)

	@quotes.command()
	@commands.guild_only()
	async def search_quotes_author(self, ctx: discord.ApplicationContext, quote_author: discord.User, page: int = 0):
		"""Search quotes by author. Lists up to ten per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		total_quotes = 0

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "search_quotes_author")
		if not failedPermissionCheck:
			embed, total_quotes = await QuoteUtils.handle_searching_author(ctx, self.mph, page, embed, quote_author.id)

		view = SearchQuotesView(ctx, self.mph, page, total_quotes, SearchTypes.AUTHOR, quote_author.id, None)

		if page <= 0:
			view.previous_page.disabled = True
		if page >= math.ceil(total_quotes / 10) - 1:
			view.next_page.disabled = True

		await ctx.respond(embed=embed, view=view)
		await self.mph.update_management_portal_command_used("quotes", "search_quotes_author", ctx.guild.id)

	@quotes.command()
	@commands.guild_only()
	async def search_quotes_text(self, ctx: discord.ApplicationContext, text: str, page: int = 0):
		"""Search quotes by text. Lists up to ten per page."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		total_quotes = 0

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "search_quotes_text")
		if not failedPermissionCheck:
			embed, total_quotes = await QuoteUtils.handle_searching_content(ctx, self.mph, page, embed, text)

		view = SearchQuotesView(ctx, self.mph, page, total_quotes, SearchTypes.CONTENT, None, text)

		if page <= 0:
			view.previous_page.disabled = True
		if page >= math.ceil(total_quotes / 10) - 1:
			view.next_page.disabled = True

		await ctx.respond(embed=embed, view=view)
		await self.mph.update_management_portal_command_used("quotes", "search_quotes_text", ctx.guild.id)

	@quotes.command()
	@commands.guild_only()
	async def list_recent_quotes(self, ctx: discord.ApplicationContext):
		"""List ten of the most recent quotes"""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "quotes", "list_recent_quotes")
		if not failedPermissionCheck:

			# Get the quotes
			response = await self.mph.quotes.list_recent_quotes(ctx.guild.id)
			quotes = response["quotes"]

			# Check if the response is empty
			if len(quotes) == 0:
				embed.title = "No Quotes Found"
				embed.description = "No quotes have been added yet."
			else:
				embed.title = "Recent Quotes"

				# Add the quotes to the embed
				for quote in quotes:
					embed.add_field(name="Quote #" + str(quote["quote_number"]), value=quote["content"])

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("quotes", "list_recent_quotes", ctx.guild.id)
