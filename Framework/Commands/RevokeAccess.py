from discord.ext import commands
import discord
from ..GeneralUtilities import CommandAccess
from ..GeneralUtilities import GeneralUtilities as Utilities
import json


class RevokeAccess(commands.Cog):

	@commands.command(name='revokeCommandAccess')
	@commands.guild_only()
	async def revoke_command_access(self, ctx, user=None, command=None):
		"""Revoke access to a specific command. Only available to TitanBot Wizards."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("moderator"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "moderator"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "revokeCommandAccess"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have access to use this command."
		elif await CommandAccess.check_user_is_wizard(ctx) is None:
			embed.title = "Cannot use this command"
			embed.description = "You do not have access to use this command."
		else:
			# Ensure the user and command arguments are provided
			if user is None or command is None:
				embed.title = "Failed to revoke command access"
				embed.description = "You must specify a user to remove permissions from, and the command to affect."
			else:
				user = str(user)
				command = str(command)

				with open(Utilities.get_revoked_commands_directory(), 'r') as f:
					data = json.load(f)

				maxIndex = 0
				userData = None
				userDataIndex = 0
				# Check for existing user data
				for _ in data:
					if user in data[maxIndex]["user"]:
						userData = data[maxIndex]
						userDataIndex = maxIndex
					maxIndex = maxIndex + 1

				# If data does exist...
				embed.title = "User Access Changed: " + command
				if userData is not None:
					# Check if the command is already in the database,
					#  if so, remove it. Otherwise, add it.
					if command in userData["revokedCommands"]:
						# Remove the command from the data at our position
						data[userDataIndex]["revokedCommands"].remove(command)
						# If it's the last command in the data, remove the entire entry
						if len(userData["revokedCommands"]) == 0:
							data.pop(userDataIndex)
						embed.description = "Access to the command has been restored to the user."
					else:
						data[userDataIndex]["revokedCommands"].append(command)
						embed.description = "Access to the command has been revoked from the user."
				else:
					# Make a new entry in the database
					dictionary = {"user": user, "revokedCommands": [command]}
					data.append(dictionary)
					embed.description = "Access to the command has been revoked from the user."

				with open(Utilities.get_revoked_commands_directory(), 'w') as f:
					json.dump(data, f, indent=4)

		await ctx.send(embed=embed)

	@commands.command(name='viewRevokedCommands')
	@commands.guild_only()
	async def view_revoked_commands(self, ctx, user=None):
		"""See revoked commands for a user. Defaults to the author of the message if no user is provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("moderator"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "moderator"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "viewRevokedCommands"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			# Check if a user is provided
			if user is None:
				user = ctx.message.author.mention
			user = user.lstrip("<@!").rstrip(">")

			with open(Utilities.get_revoked_commands_directory(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			userData = None
			# Check for existing user data
			for _ in data:
				if user in data[maxIndex]["user"]:
					userData = data[maxIndex]
				maxIndex = maxIndex + 1

			userForDisplay = await ctx.bot.fetch_user(int(user))
			embed.title = "Command Access for " + userForDisplay.display_name
			if userData is None:
				embed.description = "No commands have been revoked from this user."
			else:
				embed.description = "Listing revoked commands:\n"
				embed.description += str(userData["revokedCommands"])

			await ctx.send(embed=embed)

	@commands.command(name='revokeModuleAccess')
	@commands.guild_only()
	async def revoke_module_access(self, ctx, user=None, module=None):
		"""Revoke access to an entire module. Only available to TitanBot Wizards."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("moderator"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "moderator"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "revokeModuleAccess"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have access to use this command."
		elif await CommandAccess.check_user_is_wizard(ctx) is None:
			embed.title = "Cannot use this command"
			embed.description = "You do not have access to use this command."
		else:
			# Ensure the user and module arguments are provided
			if user is None or module is None:
				embed.title = "Failed to revoke module access"
				embed.description = "You must specify a user to remove permissions from, and the module to affect."
			else:
				user = str(user)
				module = str(module)

				with open(Utilities.get_revoked_modules_directory(), 'r') as f:
					data = json.load(f)

				maxIndex = 0
				userData = None
				userDataIndex = 0
				# Check for existing user data
				for _ in data:
					if user in data[maxIndex]["user"]:
						userData = data[maxIndex]
						userDataIndex = maxIndex
					maxIndex = maxIndex + 1

				# If data does exist...
				embed.title = "User Access Changed: " + module
				if userData is not None:
					# Check if the module is already in the database,
					#  if so, remove it. Otherwise, add it.
					if module in userData["revokedModules"]:
						# Remove the module from the data at our position
						data[userDataIndex]["revokedModules"].remove(module)
						# If it's the last module in the data, remove the entire entry
						if len(userData["revokedModules"]) == 0:
							data.pop(userDataIndex)
						embed.description = "Access to the module has been restored to the user."
					else:
						data[userDataIndex]["revokedCommands"].append(module)
						embed.description = "Access to the module has been revoked from the user."
				else:
					# Make a new entry in the database
					dictionary = {"user": user, "revokedModules": [module]}
					data.append(dictionary)
					embed.description = "Access to the module has been revoked from the user."

				with open(Utilities.get_revoked_modules_directory(), 'w') as f:
					json.dump(data, f, indent=4)

		await ctx.send(embed=embed)

	@commands.command(name='viewRevokedModules')
	@commands.guild_only()
	async def view_revoked_modules(self, ctx, user=None):
		"""See revoked modules for a user. Defaults to the author of the message if no user is provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("moderator"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "moderator"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "viewRevokedModules"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			# Check if a user is provided
			if user is None:
				user = ctx.message.author.mention
			user = user.lstrip("<@!").rstrip(">")

			with open(Utilities.get_revoked_modules_directory(), 'r') as f:
				data = json.load(f)

			maxIndex = 0
			userData = None
			# Check for existing user data
			for _ in data:
				if user in data[maxIndex]["user"]:
					userData = data[maxIndex]
				maxIndex = maxIndex + 1

			userForDisplay = await ctx.bot.fetch_user(int(user))
			embed.title = "Module Access for " + userForDisplay.display_name
			if userData is None:
				embed.description = "No modules have been revoked from this user."
			else:
				embed.description = "Listing revoked modules:\n"
				embed.description += str(userData["revokedModules"])

			await ctx.send(embed=embed)
