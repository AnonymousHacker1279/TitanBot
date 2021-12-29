import json
from discord.ext import commands
import discord
from ..GeneralUtilities import GeneralUtilities as Utilities
from ..GeneralUtilities import CommandAccess


class UserConfig(commands.Cog):
	"""Custom configuration for each user."""

	@commands.command(name='togglePings')
	@commands.guild_only()
	async def module_info(self, ctx, status=None):
		"""Toggle pings from bot responses. Pass 'status' to see your current status."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("userConfig"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "userConfig"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "togglePings"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			embed.title = "Toggle Pings"

			# Open the settings file
			with open(Utilities.get_user_config_disabled_pings_directory(), 'r') as f:
				data = json.load(f)

			if str(status) == "status":
				# Set the title
				embed.title = "View User Configuration: Pings"
				# Get status
				line = "Current Ping Status: "
				if ctx.message.author.mention in data["disabledPings"]:
					line += "Disabled :negative_squared_cross_mark:"
				else:
					line += "Enabled :white_check_mark:"

				embed.description = line + "\n"
			elif status is None:
				# Set the title
				embed.title = "Toggle User Configuration: Pings"
				# Get status
				if ctx.message.author.mention in data["disabledPings"]:
					data["disabledPings"].remove(ctx.message.author.mention)
					line = "Bot pings are now enabled."
				else:
					data["disabledPings"].append(ctx.message.author.mention)
					line = "Bot pings are now disabled."

				with open(Utilities.get_user_config_disabled_pings_directory(), 'w') as f:
					json.dump(data, f, indent=4)

				embed.description = line + "\n"
			else:
				embed.description = "Invalid argument passed, see ``$help togglePings``."

		await ctx.send(embed=embed)
