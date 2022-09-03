import json
import os
from datetime import datetime
from os.path import isfile

import discord
from discord.ext import commands

from .Modals import CustomCommandModals
from ..FileSystemAPI import DatabaseObjects
from ..GeneralUtilities import GeneralUtilities, OsmiumInterconnect, \
	PermissionHandler


class CustomCommands(commands.Cog):
	"""Expand the power of TitanBot with custom commands."""

	@commands.slash_command(name="custom_command")
	@commands.guild_only()
	async def custom_command(self, ctx: discord.ApplicationContext, command_name: str, args: str = None):
		"""Execute a custom command."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='Executing your command, please be patient...')
		await ctx.respond(embed=embed)

		path = await DatabaseObjects.get_custom_commands_directory(ctx.guild_id) + "\\" + command_name + ".js"
		if args is None:
			args = ""
		args = await GeneralUtilities.arg_splitter(args)

		with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild_id), "r") as f:
			metadata = json.load(f)
			wizard_only = False
			if command_name in metadata["wizard_only_commands"]:
				wizard_only = True

		if isfile(path):
			embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																					command_name,
																					shouldCheckForWizard=wizard_only)
			if not failedPermissionCheck:
				with open(path, "r") as f:
					embed = await OsmiumInterconnect.execute_with_osmium(f.read(), args, embed)
		else:
			try:
				path = await DatabaseObjects.get_custom_commands_directory(ctx.guild_id) + "\\" + metadata["aliases"][
					command_name] + ".js"
				embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																					command_name,
																					shouldCheckForWizard=wizard_only)
				if not failedPermissionCheck:
					with open(path, "r") as f:
						embed = await OsmiumInterconnect.execute_with_osmium(f.read(), args, embed)

			except (ValueError, TypeError, KeyError):
				embed.title = "Command Not Found"
				embed.description = "A matching command could not be found.\n\n"

		await ctx.edit(embed=embed)

	@commands.slash_command(name="add_command")
	async def add_command(self, ctx: discord.ApplicationContext):
		"""Add a custom command to the archive."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"add_command",
																				shouldCheckForWizard=True)
		if not failedPermissionCheck:
			modal = CustomCommandModals.AddCommand(title="Add a custom command")
			await ctx.send_modal(modal)

	@commands.slash_command(name='remove_command')
	@commands.guild_only()
	async def remove_command(self, ctx: discord.ApplicationContext, command_name: str = None):
		"""Remove a custom command from the archive."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"remove_command",
																				shouldCheckForWizard=True)
		if not failedPermissionCheck:
			if command_name is not None:
				path = await DatabaseObjects.get_custom_commands_directory(ctx.guild_id) + "/" + command_name + ".js"
				if isfile(path):
					os.remove(path)

				with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild_id), 'r') as f:
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
					with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild_id), 'w') as f:
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

		await ctx.respond(embed=embed)

	@commands.slash_command(name='command_info')
	@commands.guild_only()
	async def command_info(self, ctx: discord.ApplicationContext, command_name: str = None):
		"""Get information about a custom command."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"command_info")
		if not failedPermissionCheck:
			if command_name is not None:
				with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild_id), 'r') as f:
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

		await ctx.respond(embed=embed)
