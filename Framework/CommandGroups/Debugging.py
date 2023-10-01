import discord
from discord.ext import commands

from ..GeneralUtilities import PermissionHandler


class Debugging(commands.Cog):
	"""Debug only commands."""

	debugging = discord.SlashCommandGroup("debugging", description="Debug only commands", guild_ids=[1025825210005475408])

	def __init__(self, management_portal_handler):
		self.mph = management_portal_handler

	@debugging.command()
	@commands.guild_only()
	async def speak_debug_only(self, ctx: discord.ApplicationContext, message: str, channel: str = None, hide_user: bool = False):
		"""Make the bot say something in a channel. Debug only, allows any channel ID."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "fun", "speak")
		if not failedPermissionCheck:
			user = ctx.author

			if channel is None:
				channel = ctx.channel
			else:
				# lookup channel by id
				channel = ctx.bot.get_channel(int(channel))

			try:
				send_failed = False
				if hide_user:
					if user.guild_permissions.administrator or PermissionHandler.is_superuser(self.mph, user.id):
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
