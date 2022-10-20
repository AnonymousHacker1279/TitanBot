import json

import discord
from discord.ext import commands
from discord.ext.bridge import bot

from ..FileSystemAPI import DatabaseObjects
from ..GeneralUtilities import CommandAccess, GeneralUtilities, PermissionHandler


class RevokeAccess(commands.Cog):
	"""Limit feature access for users who misbehave."""

	def __init__(self, management_portal_handler):
		self.mph = management_portal_handler

	@bot.bridge_command(aliases=["rca"])
	@commands.guild_only()
	async def revoke_command_access(self, ctx: discord.ApplicationContext, user=None, command=None):
		"""Revoke access to a specific command. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "access_control", "revoke_command_access", True)
		if not failedPermissionCheck:
			# Ensure the user and command arguments are provided
			if user is None or command is None:
				embed.title = "Failed to revoke command access"
				embed.description = "You must specify a user to remove permissions from, and the command to affect."
			else:
				user = str(user)
				command = str(command)

				cache_manager = CommandAccess.cache_managers["revoked_modules"].get(ctx.guild.id)
				data = await cache_manager.get_cache()

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

				with open(await DatabaseObjects.get_revoked_commands_database(ctx.guild.id), 'w') as f:
					json.dump(data, f, indent=4)

				await cache_manager.invalidate_cache()

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("access_control", "revoke_command_access", ctx.guild.id)

	@bot.bridge_command(aliases=["vrc"])
	@commands.guild_only()
	async def view_revoked_commands(self, ctx: discord.ApplicationContext, user=None):
		"""See revoked commands for a user. Defaults to the author of the message if no user is provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "access_control", "view_revoked_commands")
		if not failedPermissionCheck:
			# Check if a user is provided
			if user is None:
				user = ctx.author.mention
			user = await GeneralUtilities.strip_usernames(user)

			cache_manager = CommandAccess.cache_managers["revoked_modules"].get(ctx.guild.id)
			data = await cache_manager.get_cache()

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

			await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("access_control", "view_revoked_commands", ctx.guild.id)

	@bot.bridge_command(aliases=["rma"])
	@commands.guild_only()
	async def revoke_module_access(self, ctx: discord.ApplicationContext, user=None, module=None):
		"""Revoke access to an entire module. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "access_control", "revoke_module_access", True)
		if not failedPermissionCheck:
			# Ensure the user and module arguments are provided
			if user is None or module is None:
				embed.title = "Failed to revoke module access"
				embed.description = "You must specify a user to remove permissions from, and the module to affect."
			else:
				user = str(user)
				module = str(module)

				cache_manager = CommandAccess.cache_managers["revoked_modules"].get(ctx.guild.id)
				data = await cache_manager.get_cache()

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

				with open(await DatabaseObjects.get_revoked_modules_database(ctx.guild.id), 'w') as f:
					json.dump(data, f, indent=4)

				await cache_manager.invalidate_cache()

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("access_control", "revoke_module_access", ctx.guild.id)

	@bot.bridge_command(aliases=["vrm"])
	@commands.guild_only()
	async def view_revoked_modules(self, ctx: discord.ApplicationContext, user=None):
		"""See revoked modules for a user. Defaults to the author of the message if no user is provided."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "access_control", "view_revoked_modules")
		if not failedPermissionCheck:
			# Check if a user is provided
			if user is None:
				user = ctx.author.mention
			user = await GeneralUtilities.strip_usernames(user)

			cache_manager = CommandAccess.cache_managers["revoked_modules"].get(ctx.guild.id)
			data = await cache_manager.get_cache()

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

			await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("access_control", "view_revoked_modules", ctx.guild.id)
