import discord
from discord import Spotify
from discord.ext import commands

from ..GeneralUtilities import PermissionHandler


class Fun(commands.Cog):
	"""Have fun with some useless commands."""

	@commands.command(name='stab')
	@commands.guild_only()
	async def stab(self, ctx, user=None):
		"""Stab someone, or something."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "stab")
		if not failedPermissionCheck:
			if user is None:
				embed.title = "Failed to stab"
				embed.description = "You have to tell me who you want to stab."
			else:
				embed.title = "A BLOODY MASSACRE"
				embed.description = "*" + user + " was stabbed by " + ctx.message.author.mention + "*"

		await ctx.send(embed=embed)

	@commands.command(name='spotify')
	@commands.guild_only()
	async def spotify(self, ctx, user=None):
		"""Check the status of a user playing music via Spotify. Specify a user, otherwise uses the user executing the command."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "spotify")
		if not failedPermissionCheck:
			if user is None:
				user = ctx.author
			if user.activities:
				for activity in user.activities:
					if isinstance(activity, Spotify):
						embed.title = f"{user.name}'s Spotify"
						embed.description = "Listening to **{}".format(activity.title) + "**"
						embed.set_thumbnail(url=activity.album_cover_url)
						embed.add_field(name="Artist", value=activity.artist)
						embed.add_field(name="Album", value=activity.album)
						embed.add_field(name="Duration", value=str(activity.duration).split(".")[0])
						embed.set_footer(text="Track ID: {}".format(activity.track_id))
			else:
				embed.title = "Cannot get Spotify status"
				embed.description = "The user is not listening to Spotify."

		await ctx.send(embed=embed)
