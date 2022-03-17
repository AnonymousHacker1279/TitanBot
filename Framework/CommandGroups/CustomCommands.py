import json
import os
from os.path import isfile

import discord
import requests
from discord.ext import commands

from ..GeneralUtilities import Constants, OsmiumInterconnect, PermissionHandler, VirusTotalQuery
from ..GeneralUtilities import GeneralUtilities as Utilities


class CustomCommands(commands.Cog):
	"""Expand the power of TitanBot with custom commands."""

	@commands.command(name='addCommand', aliases=["ac"])
	@commands.guild_only()
	async def add_command(self, ctx, command_name: str = None, alias: str = None, wizard_only: bool = False,
							code: str = None):
		"""Add a custom command to the archive."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"addCommand",
																				shouldCheckForWizard=True)
		if not failedPermissionCheck:
			if command_name is not None:
				if code is None:
					try:
						file_url = ctx.message.attachments[0]
						file_contents = requests.get(file_url).text
						code = file_contents
					except (ValueError, IndexError):
						embed.title = "Failed to Add Custom Command"
						embed.description = "You must provide code to run with the command."
				if code is not None:
					# Scan the code for malware unless disabled
					message = None
					if Constants.ENABLE_CUSTOM_COMMANDS_MALWARE_SCANNING == "True":
						embed.title = "Command Addition Pending"
						embed.description = "Your command is currently being scanned for malware via VirusTotal. " \
											"This process can take some time, so please be patient."
						embed.set_footer(text="This window will automatically update once the scan is complete.")
						message = await ctx.send(embed=embed)
						scan_result = await VirusTotalQuery.scan_text(code)
						if scan_result["THREAT"]:
							embed.title = "Refusing to Add Custom Command: Malware Detected"
							embed.description = "A malware scan via VirusTotal determined the submitted code to be **malicious**." \
												"\n```txt\nMalware Name: " + scan_result["THREAT_NAME"] + "\nSHA-256 Hash: " \
												"" + scan_result["SHA256"] + "\n```\nThe scan result can be found below:\n" \
												"https://www.virustotal.com/gui/file/" + scan_result["SHA256"]

							embed.set_footer(text="Think something is wrong? Please contact an administrator.")
							await message.edit(embed=embed)
					else:
						scan_result = {"THREAT": False}

					if scan_result["THREAT"] is False:
						with open(await Utilities.get_custom_commands_directory() + "/" + command_name + ".js", 'w') as f:
							f.write(code)
						with open(await Utilities.get_custom_commands_metadata_database(), 'r') as f:
							metadata_database = json.load(f)
						with open(await Utilities.get_custom_commands_metadata_database(), 'w') as f:
							metadata_database["aliases"][alias] = command_name
							if wizard_only:
								metadata_database["wizard_only_commands"].append(command_name)
							json.dump(metadata_database, f, indent=4)

						embed.title = "Custom Command Added: " + command_name
						embed.description = "You can now run the custom command by typing `$" + command_name + "`" \
											" or by using the alias `$" + alias + "`"
						embed.set_footer(text="")
						if message is not None:
							await message.edit(embed=embed)
						else:
							await ctx.send(embed=embed)
				else:
					embed.title = "Failed to Add Custom Command"
					embed.description = "You must provide code to run with the command."
					await ctx.send(embed=embed)
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

				with open(await Utilities.get_custom_commands_metadata_database(), 'r') as f:
					metadata_database = json.load(f)

					database_commands_list = []
					database_alias_list = []
					for item in metadata_database["aliases"]:
						database_alias_list.append(item)
						database_commands_list.append(metadata_database["aliases"][item])

					command_index_position = database_commands_list.index(command_name)
					alias = database_alias_list[command_index_position]

				with open(await Utilities.get_custom_commands_metadata_database(), 'w') as f:
					metadata_database["aliases"].pop(alias)
					if command_name in metadata_database["wizard_only_commands"]:
						metadata_database["wizard_only_commands"].remove(command_name)
					json.dump(metadata_database, f, indent=4)

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
