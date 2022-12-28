import re
from datetime import datetime

import discord
from discord.errors import HTTPException, NotFound


async def prepare_quote(ctx, embed, author, content, quoteID, date, quotedBy) -> discord.Embed:
	embed.title = "Quote #" + quoteID

	links = re.findall('https://[a-zA-Z0-9-./_&]*', content)
	contentExcludingLinks = ""
	iteration = 0

	if date != "1970-01-01 00:00:00":
		iso_date = datetime.fromisoformat(date)
		readable_date = str(iso_date.month) + "/" + str(iso_date.day) + "/" + str(iso_date.year) \
						+ " at " + str(iso_date.hour) + \
						":" + str(iso_date.minute) + ":" + str(iso_date.second)
	else:
		readable_date = "Unknown"
		quotedBy = "Unknown"

	try:
		int(quotedBy)
		quoted_by_user = str(await ctx.bot.fetch_user(quotedBy))
	except ValueError:
		quoted_by_user = quotedBy

	try:
		author_user = await ctx.bot.fetch_user(author)
		embed.set_thumbnail(url=author_user.display_avatar.url)
		author_user = author_user.mention
	except (HTTPException, NotFound, ValueError):
		embed.set_footer(text="Cannot get the profile picture for this user, try using a mention")
		author_user = str(author)

	for _ in links:
		contentExcludingLinks = re.sub(pattern=links[iteration], repl="", string=content)
		iteration += 1
	if len(links) != 0:
		if contentExcludingLinks == "":
			embed.set_image(url=links[0])
			embed.description = author_user
			embed.set_footer(text="Added " + readable_date + " by " + quoted_by_user)
		else:
			embed.description = '> "' + contentExcludingLinks + '"\n'
			embed.description += " - " + author_user
			embed.set_image(url=links[0])
			embed.set_footer(text="Added " + str(readable_date) + " by " + quoted_by_user)
	else:
		embed.description = '> "' + content + '"\n'
		embed.description += " - " + author_user
		embed.set_footer(text="Added " + str(readable_date) + " by " + quoted_by_user)

	return embed
