import json

import discord
from discord.ext import commands

from ..GeneralUtilities import GeneralUtilities as Utilities, PermissionHandler


class UserConfig(commands.Cog):
	"""Custom configuration for each user. Note: These commands currently have no use and may be removed in the future!"""

	@commands.command(name='togglePings', aliases=["tp"])
	@commands.guild_only()
	async def module_info(self, ctx, status=None):
		"""Toggle pings from bot responses. Pass 'status' to see your current status."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "userConfig", "togglePings")
		if not failedPermissionCheck:
			embed.title = "Toggle Pings"

			# Open the settings file
			with open(await Utilities.get_user_config_disabled_pings_database(), 'r') as f:
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

				with open(await Utilities.get_user_config_disabled_pings_database(), 'w') as f:
					json.dump(data, f, indent=4)

				embed.description = line + "\n"
			else:
				embed.description = "Invalid argument passed, see ``$help togglePings``."

		await ctx.send(embed=embed)
