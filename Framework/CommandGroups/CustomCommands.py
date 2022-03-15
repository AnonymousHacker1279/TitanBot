import json
import os
from os.path import isfile

import discord
from discord.ext import commands

from ..GeneralUtilities import OsmiumInterconnect, PermissionHandler, VirusTotalQuery
from ..GeneralUtilities import GeneralUtilities as Utilities


class CustomCommands(commands.Cog):
	"""Expand the power of TitanBot with custom commands."""

	@commands.command(name='addCommand', aliases=["ac"])
	@commands.guild_only()
	async def add_command(self, ctx, command_name: str = None, alias: str = None, code: str = None):
		"""Add a custom command to the archive."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"addCommand",
																				shouldCheckForWizard=True)
		if not failedPermissionCheck:
			if command_name is not None:
				if code is not None:
					# Scan the code for malware first
					scan_result = await VirusTotalQuery.scan_text(code)
					if scan_result["THREAT"]:
						embed.title = "Refusing to Add Custom Command: Malware Detected"
						embed.description = "A malware scan via VirusTotal determined the submitted code to be **malicious**." \
											"\n```txt\nMalware Name: " + scan_result["THREAT_NAME"] + "\nSHA-256 Hash: " \
											"" + scan_result["SHA256"] + "\n```\nThe scan result can be found below:\n" \
											"https://www.virustotal.com/gui/file/" + scan_result["SHA256"]

						embed.set_footer(text="Think something is wrong? Please contact an administrator.")

					if scan_result["THREAT"] is False:
						with open(await Utilities.get_custom_commands_directory() + "/" + command_name + ".js", 'w') as f:
							f.write(code)
						with open(await Utilities.get_custom_commands_alias_database(), 'r') as f:
							alias_database = json.load(f)
						with open(await Utilities.get_custom_commands_alias_database(), 'w') as f:
							alias_database["aliases"][alias] = command_name
							json.dump(alias_database, f, indent=4)

						embed.title = "Custom Command Added: " + command_name
						embed.description = "You can now run the custom command by typing `$" + command_name + "`" \
											" or by using the alias `$" + alias + "`"
				else:
					embed.title = "Failed to Add Custom Command"
					embed.description = "You must provide code to run with the command."
			else:
				embed.title = "Failed to Add Custom Command"
				embed.description = "You must specify a command name."

		await ctx.send(embed=embed)

	@commands.command(name='removeCommand', aliases=["rc"])
	@commands.guild_only()
	async def remove_command(self, ctx, command_name: str = None):
		"""Remove a custom command from the archive."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"removeCommand",
																				shouldCheckForWizard=True)
		if not failedPermissionCheck:
			if command_name is not None:
				path = await Utilities.get_custom_commands_directory() + "/" + command_name + ".js"
				if isfile(path):
					os.remove(path)

				with open(await Utilities.get_custom_commands_alias_database(), 'r') as f:
					alias_database = json.load(f)

					database_commands_list = []
					database_alias_list = []
					for item in alias_database["aliases"]:
						database_alias_list.append(item)
						database_commands_list.append(alias_database["aliases"][item])

					command_index_position = database_commands_list.index(command_name)
					alias = database_alias_list[command_index_position]

				with open(await Utilities.get_custom_commands_alias_database(), 'w') as f:
					alias_database["aliases"].pop(alias)
					json.dump(alias_database, f, indent=4)

				embed.title = "Custom Command Removed: " + command_name
				embed.description = "The custom command and its aliases have been removed."

			else:
				embed.title = "Failed to Remove Custom Command"
				embed.description = "You must specify a command name to remove."

		await ctx.send(embed=embed)

	@commands.command(name='runJS', aliases=["rj"])
	@commands.guild_only()
	async def run_javascript(self, ctx, code: str = None):
		"""Directly execute a block of JavaScript. Useful for testing new commands."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"runJS", shouldCheckForWizard=True)
		if not failedPermissionCheck:
			if code is not None:
				embed = await OsmiumInterconnect.execute_with_osmium(code, arguments=[], embed=embed)
			else:
				embed.title = "Failed to execute JavaScript"
				embed.description = "You must provide a block of code to be executed."

		await ctx.send(embed=embed)
