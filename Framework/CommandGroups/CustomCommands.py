import json
import os
from datetime import datetime
from os.path import isfile

import discord
from discord.ext import commands
from discord.ext.bridge import bot

from .Modals import CustomCommandModals
from ..FileSystemAPI import DatabaseObjects
from ..GeneralUtilities import GeneralUtilities, OsmiumInterconnect, \
	PermissionHandler


class CustomCommands(commands.Cog):
	"""Expand the power of TitanBot with custom commands."""

	def __init__(self, management_portal_handler):
		self.mph = management_portal_handler

	@bot.bridge_command(aliases=["cc"])
	@commands.guild_only()
	async def custom_command(self, ctx: discord.ApplicationContext, command_name: str, args: str = None):
		"""Execute a custom command."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='Executing your command, please be patient...')
		await ctx.respond(embed=embed)

		path = await DatabaseObjects.get_custom_commands_directory(ctx.guild.id) + "\\" + command_name + ".js"
		if args is None:
			args = ""
		args = await GeneralUtilities.arg_splitter(args)

		with open(await DatabaseObjects.get_custom_commands_metadata_database(ctx.guild.id), "r") as f:
			metadata = json.load(f)
			admin_only = False
			if command_name in metadata["admin_only_commands"]:
				admin_only = True

		if isfile(path):
			embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																					command_name,
																					shouldCheckForAdmin=admin_only)
			if not failedPermissionCheck:
				with open(path, "r") as f:
					embed = await OsmiumInterconnect.execute_with_osmium(self.mph, ctx.guild.id, f.read(), args, embed)
		else:
			try:
				path = await DatabaseObjects.get_custom_commands_directory(ctx.guild.id) + "\\" + metadata["aliases"][
					command_name] + ".js"
				embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																					command_name,
																					shouldCheckForAdmin=admin_only)
				if not failedPermissionCheck:
					with open(path, "r") as f:
						embed = await OsmiumInterconnect.execute_with_osmium(self.mph, ctx.guild.id, f.read(), args, embed)

			except (ValueError, TypeError, KeyError):
				embed.title = "Command Not Found"
				embed.description = "A matching command could not be found.\n\n"

		await ctx.edit(embed=embed)
		await self.mph.update_management_portal_command_used("customCommands", command_name, ctx.guild.id)

	@bot.bridge_command(aliases=["ac"])
	@commands.guild_only()
	async def add_command(self, ctx: discord.ApplicationContext):
		"""Add a custom command to the archive."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"add_command",
																				shouldCheckForAdmin=True)
		if not failedPermissionCheck:
			enable_vt_scanning = await self.mph.cm.get_guild_specific_value(ctx.guild.id, "enable_custom_commands_malware_scanning")
			modal = CustomCommandModals.AddCommand(title="Add a custom command", vt_scan_enabled=enable_vt_scanning)
			await ctx.send_modal(modal)
			await self.mph.update_management_portal_command_used("customCommands", "add_command", ctx.guild.id)

	@bot.bridge_command(aliases=["rc"])
	@commands.guild_only()
	async def remove_command(self, ctx: discord.ApplicationContext, command_name: str = None):
		"""Remove a custom command from the archive."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"remove_command",
																				shouldCheckForAdmin=True)
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
						if command_name in metadata_database["admin_only_commands"]:
							metadata_database["admin_only_commands"].remove(command_name)
						metadata_database["metadata"].pop(command_name)
						json.dump(metadata_database, f, indent=4)

					embed.title = "Custom Command Removed: " + command_name
					embed.description = "The custom command and its aliases have been removed."

			else:
				embed.title = "Failed to Remove Custom Command"
				embed.description = "You must specify a command name to remove."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("customCommands", "remove_command", ctx.guild.id)

	@bot.bridge_command(aliases=["cmdi"])
	@commands.guild_only()
	async def command_info(self, ctx: discord.ApplicationContext, command_name: str = None):
		"""Get information about a custom command."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"command_info")
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

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("customCommands", "command_info", ctx.guild.id)
