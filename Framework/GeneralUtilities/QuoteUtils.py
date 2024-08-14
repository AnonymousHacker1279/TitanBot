import math
import re
from datetime import datetime

import discord
from discord.errors import HTTPException, NotFound

from Framework.SQLBridge import SQLBridge


async def prepare_quote(ctx: discord.ApplicationContext, embed: discord.Embed, author: int, content: str, quote_id: int, date: str, quoted_by: int) -> discord.Embed:
	"""
	Prepare a quote for display in an embed.
	
	:param ctx: The context of the command.
	:param embed: The embed to prepare.
	:param author: The author of the quote.
	:param content: The content of the quote.
	:param quote_id: The ID of the quote.
	:param date: The date the quote was added.
	:param quoted_by: The user who added the quote.
	"""

	embed.title = "Quote #" + str(quote_id)

	links = re.findall('https://[a-zA-Z0-9-./_&]*', content)
	content_excluding_links = ""
	iteration = 0

	if date != "1970-01-01 00:00:00":
		iso_date = datetime.fromisoformat(date)
		readable_date = str(iso_date.month) + "/" + str(iso_date.day) + "/" + str(iso_date.year) \
						+ " at " + str(iso_date.hour) + \
						":" + str(iso_date.minute) + ":" + str(iso_date.second)
	else:
		readable_date = "Unknown"
		quoted_by = "Unknown"

	try:
		int(quoted_by)
		quoted_by_user = str(await ctx.bot.fetch_user(quoted_by))
	except ValueError:
		quoted_by_user = quoted_by

	try:
		author_user = await ctx.bot.fetch_user(author)
		embed.set_thumbnail(url=author_user.display_avatar.url)
		author_user = author_user.mention
	except (HTTPException, NotFound, ValueError):
		embed.set_footer(text="Cannot get the profile picture for this user, try using a mention")
		author_user = str(author)

	for _ in links:
		content_excluding_links = re.sub(pattern=links[iteration], repl="", string=content)
		iteration += 1
	if len(links) != 0:
		if content_excluding_links == "":
			embed.set_image(url=links[0])
			embed.description = author_user
			embed.set_footer(text="Added " + readable_date + " by " + quoted_by_user)
		else:
			embed.description = '> "' + content_excluding_links + '"\n'
			embed.description += " \\- " + author_user
			embed.set_image(url=links[0])
			embed.set_footer(text="Added " + str(readable_date) + " by " + quoted_by_user)
	else:
		embed.description = '> "' + content + '"\n'
		embed.description += " \\- " + author_user
		embed.set_footer(text="Added " + str(readable_date) + " by " + quoted_by_user)

	return embed


async def handle_searching_author(ctx: discord.ApplicationContext, bridge: SQLBridge, page: int, embed: discord.Embed, quote_author: int, descending_order: bool = False) -> tuple[discord.Embed, int]:
	"""
	Handle searching for quotes by a specific author.

	:param ctx: The context of the command.
	:param bridge: The SQLBridge instance.
	:param page: The page of quotes to search for.
	:param embed: The embed to display the quotes in.
	:param quote_author: The author of the quotes.
	:param descending_order: Whether to sort the quotes descending
	"""

	if page < 0:
		embed.title = "Cannot search quotes"
		embed.description = "Invalid page. The page must be greater than zero."
	else:
		author_display_name = quote_author

		# Try getting a profile picture for the author and a display name
		try:
			author_user = await ctx.bot.fetch_user(quote_author)
			author_display_name = author_user.display_name
			embed.set_thumbnail(url=author_user.display_avatar.url)
		except (NotFound, ValueError):
			embed.set_footer(text="Cannot get the profile picture for this user. Ensure the author is a valid user.")

		# Get the quotes
		quotes, total_quotes = await bridge.quotes_module.search_by_author(ctx.guild.id, quote_author, page, descending_order)

		# Check if the response is empty
		if total_quotes == 0:
			embed.title = "No Quotes Found"
			embed.description = "This author has no quotes."
		else:
			embed.title = "Quotes by " + author_display_name

			if page != 0:
				embed.title += " (Page " + str(page) + ")"

			embed.description = "There are **" + str(total_quotes) + "** quotes by this author " \
								"(page " + str(page) + " of " + str(math.ceil(total_quotes / 10) - 1) + ")."

			# Add the quotes to the embed
			for quote in quotes:
				embed.add_field(name="Quote #" + str(quote[0]), value=quote[1])

		return embed, total_quotes


async def handle_searching_content(ctx: discord.ApplicationContext, bridge: SQLBridge, page: int, embed: discord.Embed, text: str, descending_order: bool = False) -> tuple[discord.Embed, int]:
	"""
	Handle searching for quotes containing specific text.

	:param ctx: The context of the command.
	:param bridge: The SQLBridge instance.
	:param page: The page of quotes to search for.
	:param embed: The embed to display the quotes in.
	:param text: The text to search for.
	:param descending_order: Whether to sort the quotes descending
	"""

	if page < 0:
		embed.title = "Cannot search quotes"
		embed.description = "Invalid page. The page must be greater than zero."
	else:

		embed.title = "Quotes Containing '" + text + "'"

		# Get the quotes
		quotes, total_quotes = await bridge.quotes_module.search_by_text(ctx.guild.id, text, page, descending_order)

		# Check if the response is empty
		if total_quotes == 0:
			embed.title = "No Quotes Found"
			embed.description = "No quotes were found containing this text."
		else:

			if page != 0:
				embed.title += " (Page " + str(page) + ")"

			embed.description = "There are **" + str(total_quotes) + "** quotes containing this text " \
								"(page " + str(page) + " of " + str(math.ceil(total_quotes / 10) - 1) + ")."

			# Add the quotes to the embed
			for quote in quotes:
				embed.add_field(name="Quote #" + str(quote[0]), value=quote[1])

		return embed, total_quotes
