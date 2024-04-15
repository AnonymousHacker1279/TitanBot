import discord
from discord import Spotify
from discord.ext import commands

from .BasicCog import BasicCog
from ..GeneralUtilities import PermissionHandler


class Fun(BasicCog):
	"""Have fun with some miscellaneous commands."""
	
	fun = discord.SlashCommandGroup("fun", description="Have fun with some miscellaneous commands.")

	@discord.option(
		name="user",
		description="The user to stab.",
		type=discord.User,
		required=True
	)
	@fun.command()
	@commands.guild_only()
	async def stab(self, ctx: discord.ApplicationContext, user: discord.User):
		"""Stab someone, or something."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "stab")
		if not failedPermissionCheck:
			if await PermissionHandler.is_superuser(user.id):
				embed.title = "Refusing to Stab"
				embed.description = "How dare you try to stab a superuser!"
			else:
				embed.title = "A BLOODY MASSACRE"
				embed.description = "*" + user.mention + " was stabbed by " + ctx.author.mention + "*"

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("fun", "stab", ctx.guild.id)

	@discord.option(
		name="user",
		description="The user to get a Spotify status from.",
		type=discord.User,
		required=False
	)
	@fun.command()
	@commands.guild_only()
	async def spotify(self, ctx: discord.ApplicationContext, user: discord.User = None):
		"""Check the status of a user playing music via Spotify."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "spotify")
		if not failedPermissionCheck:
			if user is None:
				user = ctx.author
			nonSpotifyActivities = 0
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
		await self.update_management_portal_command_used("fun", "spotify", ctx.guild.id)

	@discord.option(
		name="message",
		description="The message to send.",
		type=str,
		required=True
	)
	@discord.option(
		name="channel",
		description="The channel to send the message in.",
		type=discord.TextChannel,
		required=False
	)
	@discord.option(
		name="hide_user",
		description="Hide the user's identity. (Admin only)",
		type=bool,
		required=False
	)
	@fun.command()
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
					if user.guild_permissions.administrator or await PermissionHandler.is_superuser(user.id):
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
		await self.update_management_portal_command_used("fun", "speak", ctx.guild.id)

	@fun.command()
	@commands.guild_only()
	async def inspirobot_query(self, ctx: discord.ApplicationContext):
		"""Generate a random image from InspiroBot."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "inspirobot_query")
		if not failedPermissionCheck:
			# Get an image URL from InspiroBot
			image_url = await self.mph.get("https://inspirobot.me/api?generate=true", non_management_portal=True)

			# Create the embed
			embed.title = "InspiroBot Query"
			embed.set_image(url=image_url)
			embed.set_footer(text="Powered by InspiroBot")

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("fun", "inspirobot_query", ctx.guild.id)

	@fun.command()
	@commands.guild_only()
	async def random_fact(self, ctx: discord.ApplicationContext):
		"""Get a random and useless, but true, fact."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "random_fact")
		if not failedPermissionCheck:
			# Get a random fact
			response = await self.mph.get("https://uselessfacts.jsph.pl/random.json?language=en", non_management_portal=True)

			# Create the embed
			embed.title = "Random Fact"
			embed.description = response["text"]
			embed.set_footer(text="Permalink: " + response["permalink"])

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("fun", "random_fact", ctx.guild.id)
		