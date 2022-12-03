import aiohttp
import discord
from discord import Spotify
from discord.ext import commands
from discord.ext.bridge import bot

from ..GeneralUtilities import GeneralUtilities, PermissionHandler


class Fun(commands.Cog):
	"""Have fun with some useless commands."""

	def __init__(self, management_portal_handler):
		self.mph = management_portal_handler

	@bot.bridge_command()
	@commands.guild_only()
	async def stab(self, ctx: discord.ApplicationContext, user=None):
		"""Stab someone, or something."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "stab")
		if not failedPermissionCheck:
			if user is None:
				embed.title = "Failed to stab"
				embed.description = "You have to tell me who you want to stab."
			else:
				embed.title = "A BLOODY MASSACRE"
				embed.description = "*" + user + " was stabbed by " + ctx.author.mention + "*"

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("fun", "stab", ctx.guild.id)

	@bot.bridge_command()
	@commands.guild_only()
	async def spotify(self, ctx: discord.ApplicationContext, user=None):
		"""Check the status of a user playing music via Spotify."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "spotify")
		if not failedPermissionCheck:
			if user is None:
				user = ctx.author
			nonSpotifyActivities = 0
			if isinstance(user, str):
				user = ctx.guild.get_member(int(await GeneralUtilities.strip_usernames(user)))
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
						nonSpotifyActivities += 1
						if nonSpotifyActivities == len(user.activities):
							embed.title = "Cannot get Spotify status"
							embed.description = "The user is not listening to Spotify."
			else:
				embed.title = "Cannot get Spotify status"
				embed.description = "The user is not listening to Spotify."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("fun", "spotify", ctx.guild.id)

	@bot.bridge_command(aliases=["spk"])
	@commands.guild_only()
	async def speak(self, ctx: discord.ApplicationContext, message: str, channel: discord.TextChannel = None, hide_user: bool = False):
		"""Make the bot say something in a channel."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "speak")
		if not failedPermissionCheck:
			user = ctx.author

			if channel is None:
				channel = ctx.channel

			try:
				send_failed = False
				if hide_user:
					if user.guild_permissions.administrator:
						await channel.send(message)
					else:
						send_failed = True
				else:
					await channel.send(f"({user.name}) " + message)

				if send_failed:
					embed.title = "Failed to speak"
					embed.description = "You do not have permission to hide your identity."
				else:
					embed.title = "Message sent"
					embed.description = f"Sent message to {channel.mention}"
			except discord.Forbidden:
				embed.title = "Failed to speak"
				embed.description = "I don't have permission to speak in that channel."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("fun", "speak", ctx.guild.id)

	@bot.bridge_command(aliases=["insp"])
	@commands.guild_only()
	async def inspirobot_query(self, ctx: discord.ApplicationContext):
		"""Generate a random image from InspiroBot."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "inspirobot_query")
		if not failedPermissionCheck:
			# Get an image URL from InspiroBot
			async with aiohttp.ClientSession() as session:
				async with session.get("https://inspirobot.me/api?generate=true") as response:
					image_url = await response.text()

			# Create the embed
			embed.title = "InspiroBot Query"
			embed.set_image(url=image_url)
			embed.set_footer(text="Powered by InspiroBot")

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("fun", "inspirobot_query", ctx.guild.id)

	@bot.bridge_command(aliases=["rfct"])
	@commands.guild_only()
	async def random_fact(self, ctx: discord.ApplicationContext):
		"""Get a random and useless, but true, fact."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "random_fact")
		if not failedPermissionCheck:
			# Get a random fact
			async with aiohttp.ClientSession() as session:
				async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as response:
					data = await response.json()

			# Create the embed
			embed.title = "Random Fact"
			embed.description = data["text"]
			embed.set_footer(text="Permalink: " + data["permalink"])

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("fun", "random_fact", ctx.guild.id)
		