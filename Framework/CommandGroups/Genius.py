import discord
from discord.ext import commands

from ..GeneralUtilities import GeniusQuery, PermissionHandler


class Genius(commands.Cog):
	"""Interact with the Genius music API."""

	genius = discord.SlashCommandGroup("genius", description="Interact with the Genius music API.")

	def __init__(self, management_portal_handler):
		self.mph = management_portal_handler

	@discord.option(
		name="artist",
		description="The artist of the song.",
		type=str,
		required=True
	)
	@discord.option(
		name="song",
		description="The name of the song.",
		type=str,
		required=True
	)
	@genius.command()
	@commands.guild_only()
	async def search(self, ctx: discord.ApplicationContext, artist: str, song: str):
		"""Search for a song by artist and song name."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "genius", "search")

		if not failedPermissionCheck:
			embed.description = "Searching Genius, please be patient..."
			await ctx.respond(embed=embed)
			await self.mph.update_management_portal_command_used("genius", "search", ctx.guild.id)

			embed.title = artist + " - " + song
			result, geniusID = await GeniusQuery.search_songs(artist, song)
			embed.description = result
			embed.set_footer(text="Genius ID: " + str(geniusID))

			await ctx.edit(embed=embed)
		else:
			await ctx.respond(embed=embed)

	@discord.option(
		name="url",
		description="The Genius URL of the song.",
		type=str,
		required=True
	)
	@genius.command()
	@commands.guild_only()
	async def get_by_url(self, ctx: discord.ApplicationContext, url: str):
		"""Search for a song by its Genius URL."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "genius", "get_by_url")

		if not failedPermissionCheck:
			embed.description = "Searching Genius, please be patient..."
			await ctx.respond(embed=embed)
			await self.mph.update_management_portal_command_used("genius", "get_by_url", ctx.guild.id)

			embed.title = "Lyrics by URL"
			result = await GeniusQuery.get_lyrics_by_url(url)
			embed.description = result

			await ctx.edit(embed=embed)
		else:
			await ctx.respond(embed=embed)

	@discord.option(
		name="song_id",
		description="The Genius ID of the song.",
		type=int,
		required=True
	)
	@genius.command()
	@commands.guild_only()
	async def get_by_id(self, ctx: discord.ApplicationContext, song_id: int):
		"""Search for a song by its Genius ID."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "genius",
																				"get_by_id")

		if not failedPermissionCheck:
			embed.description = "Searching Genius, please be patient..."
			await ctx.respond(embed=embed)
			await self.mph.update_management_portal_command_used("genius", "get_by_id", ctx.guild.id)

			embed.title = "Lyrics by ID"
			result = await GeniusQuery.get_lyrics_by_id(song_id)
			embed.description = result

			await ctx.edit(embed=embed)
		else:
			await ctx.respond(embed=embed)
