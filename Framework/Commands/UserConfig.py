import json
from discord.ext import commands
import discord
from ..GeneralUtilities import GeneralUtilities as Utilities
from ..GeneralUtilities.CommandAccess import CommandAccess

class UserConfig(commands.Cog):
	@commands.command(name='togglePings')
	@commands.guild_only()
	async def module_info(self, ctx, status=None):
		"""Toggle pings from bot responses. Pass 'status' to see your current status."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if await CommandAccess.check_module_enabled("userConfig") == False:
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
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
			elif status == None:
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

		await ctx.send(embed = embed)