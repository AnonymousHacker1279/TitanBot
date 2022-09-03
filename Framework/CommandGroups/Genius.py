import discord
from discord.ext import commands

from ..GeneralUtilities import GeniusQuery, PermissionHandler


class Genius(commands.Cog):
	"""Interact with the Genius music API."""

	@commands.slash_command(name='search_songs')
	@commands.guild_only()
	async def search_songs(self, ctx: discord.ApplicationContext, artist=None, song=None):
		"""Search for a song by artist and song name."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "genius", "search_songs")
		if not failedPermissionCheck:
			if artist is None or song is None:
				embed.title = "Genius Query Failed"
				embed.description = "You have to give me an author and song to search."
			else:
				embed.title = artist + " - " + song
				result, geniusID = await GeniusQuery.search_songs(artist, song)
				embed.description = result
				embed.set_footer(text="Genius ID: " + str(geniusID))

		await ctx.respond(embed=embed)

	@commands.slash_command(name='get_lyrics_by_url')
	@commands.guild_only()
	async def get_lyrics_by_url(self, ctx: discord.ApplicationContext, url=None):
		"""Search for a song by its Genius URL."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "genius", "get_lyrics_by_url")
		if not failedPermissionCheck:
			if url is None:
				embed.title = "Genius Query Failed"
				embed.description = "You have to give me a URL to query."
			else:
				embed.title = "Lyrics by URL"
				result = await GeniusQuery.get_lyrics_by_url(url)
				embed.description = result

		await ctx.respond(embed=embed)

	@commands.slash_command(name='get_lyrics_by_id', aliases=["lid"])
	@commands.guild_only()
	async def get_lyrics_by_id(self, ctx: discord.ApplicationContext, song_id=None):
		"""Search for a song by its Genius ID."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "genius",
																				"get_lyrics_by_id")
		if not failedPermissionCheck:
			if song_id is None:
				embed.title = "Genius Query Failed"
				embed.description = "You have to give me an ID to query."
			else:
				embed.title = "Lyrics by ID"
				result = await GeniusQuery.get_lyrics_by_id(song_id)
				embed.description = result

		await ctx.respond(embed=embed)
