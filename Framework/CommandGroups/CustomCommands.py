import json
import os
from datetime import datetime
from os.path import isfile

import discord
import requests
from discord.ext import commands

from ..FileSystemAPI import DatabaseObjects, FileAPI
from ..GeneralUtilities import Constants, GeneralUtilities as Utilities, PermissionHandler, VirusTotalQuery


class CustomCommands(commands.Cog):
	"""Expand the power of TitanBot with custom commands."""

	@commands.command(name='addCommand', aliases=["ac"])
	@commands.guild_only()
	async def add_command(self, ctx, command_name: str = None, alias: str = None, wizard_only: bool = False,
							code: str = None, description: str = None):
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
						# Minimize the code to save space
						code = await Utilities.minimize_js(code)

						file_path = os.path.abspath(await DatabaseObjects.get_custom_commands_directory(ctx.guild.id) + "/" + command_name + ".js")
						await FileAPI.create_empty_file(file_path)
						with open(file_path, 'w') as f:
							f.write(code)

						with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild.id), 'r') as f:
							metadata_database = json.load(f)

						with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild.id), 'w') as f:
							metadata_database["aliases"][alias] = command_name
							if wizard_only:
								metadata_database["wizard_only_commands"].append(command_name)

							metadata_database["metadata"][command_name] = {}
							metadata_database["metadata"][command_name]["date_added"] = datetime.now().isoformat()
							metadata_database["metadata"][command_name]["author"] = ctx.author.id
							metadata_database["metadata"][command_name]["size"] = str(len(code.encode('utf-8'))) + " bytes"

							if description is None:
								metadata_database["metadata"][command_name]["description"] = "No description provided."
							else:
								metadata_database["metadata"][command_name]["description"] = description

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
				path = await DatabaseObjects.get_custom_commands_directory(ctx.guild.id) + "/" + command_name + ".js"
				if isfile(path):
					os.remove(path)

				with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild.id), 'r') as f:
					metadata_database = json.load(f)

					database_commands_list = []
					database_alias_list = []
					for item in metadata_database["aliases"]:
						database_alias_list.append(item)
						database_commands_list.append(metadata_database["aliases"][item])

					command_exists = True

					try:
						command_index_position = database_commands_list.index(command_name)
						alias = database_alias_list[command_index_position]
					except ValueError:
						command_exists = False
						embed.title = "Failed to Get Custom Command Info"
						embed.description = "A command with the name `" + command_name + "` was not found."

				if command_exists:
					with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild.id), 'w') as f:
						metadata_database["aliases"].pop(alias)
						if command_name in metadata_database["wizard_only_commands"]:
							metadata_database["wizard_only_commands"].remove(command_name)
						metadata_database["metadata"].pop(command_name)
						json.dump(metadata_database, f, indent=4)

					embed.title = "Custom Command Removed: " + command_name
					embed.description = "The custom command and its aliases have been removed."

			else:
				embed.title = "Failed to Remove Custom Command"
				embed.description = "You must specify a command name to remove."

		await ctx.send(embed=embed)

	@commands.command(name='commandInfo', aliases=["ci"])
	@commands.guild_only()
	async def command_info(self, ctx, command_name: str = None):
		"""Get information about a custom command."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"commandInfo")
		if not failedPermissionCheck:
			if command_name is not None:
				with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild.id), 'r') as f:
					metadata = json.load(f)

					database_commands_list = []
					database_alias_list = []
					for item in metadata["aliases"]:
						database_alias_list.append(item)
						database_commands_list.append(metadata["aliases"][item])

					command_exists = True

					try:
						command_index_position = database_commands_list.index(command_name)
						alias = database_alias_list[command_index_position]
					except ValueError:
						command_exists = False
						embed.title = "Failed to Get Custom Command Info"
						embed.description = "A command with the name `" + command_name + "` was not found."

				if command_exists:
					embed.title = "Custom Command Info: " + command_name
					embed.description = metadata["metadata"][command_name]["description"]
					embed.add_field(name="Alias", value=alias, inline=False)
					date = datetime.fromisoformat(metadata["metadata"][command_name]["date_added"])
					readable_date = str(date.month) + "/" + str(date.day) + "/" + str(date.year) + " at " + str(date.hour) + \
									":" + str(date.minute) + ":" + str(date.second)
					embed.add_field(name="Date Added", value=readable_date)
					command_author = await ctx.bot.fetch_user(metadata["metadata"][command_name]["author"])
					embed.add_field(name="Author", value=command_author.mention)
					embed.add_field(name="Size", value=metadata["metadata"][command_name]["size"])

					embed.set_thumbnail(url=command_author.display_avatar.url)

			else:
				embed.title = "Failed to Get Custom Command Info"
				embed.description = "You must specify a command name to get information."

		await ctx.send(embed=embed)
