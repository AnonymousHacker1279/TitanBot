import discord


async def check_permissions(ctx, mph,
							embed: discord.Embed,
							module: str, command: str,
							shouldCheckForAdmin=False,
							shouldCheckForModuleEnabled=True,
							shouldCheckForBannedModule=True,
							shouldCheckForBannedCommand=True):

	failedPermissionCheck = False
	guild_id = ctx.guild.id

	# Check if the user is a Superuser
	if await is_superuser(mph, ctx.author.id):
		return embed, failedPermissionCheck

	if shouldCheckForModuleEnabled and not await check_module_enabled(mph, module, guild_id):
		embed.title = "Cannot use this module"
		embed.description = "This module has been disabled."
		failedPermissionCheck = True
	elif shouldCheckForBannedModule and await check_user_is_banned_from_module(mph, ctx.author.id, module, guild_id):
		embed.title = "Cannot use this module"
		embed.description = "You do not have access to use this module."
		failedPermissionCheck = True
	elif shouldCheckForBannedCommand and await check_user_is_banned_from_command(mph, ctx.author.id, module, command, guild_id):
		embed.title = "Cannot use this command"
		embed.description = "You do not have permission to use this command."
		failedPermissionCheck = True
	elif shouldCheckForAdmin and not ctx.author.guild_permissions.administrator:
		embed.title = "Cannot use this command"
		embed.description = "You do not have access to use this command."
		failedPermissionCheck = True

	return embed, failedPermissionCheck


async def is_superuser(mph, user: int) -> bool:
	# Check if a user is a superuser
	superusers = await mph.cm.get_value("superuser_list")
	return str(user) in superusers


async def check_module_enabled(mph, module: str, guild: int) -> bool:
	enabled_modules = await mph.cm.get_guild_specific_value(guild, "enabled_modules")
	return enabled_modules[module + "_enabled"]


async def check_user_is_banned_from_command(mph, user: int, module: str, command: str, guild: int) -> bool:
	# Check if a user is banned from using a command
	banned_commands = await mph.access_control.get_banned_commands(user, guild)
	return (command + "[" + module + "]") in banned_commands


async def check_user_is_banned_from_module(mph, user: int, module: str, guild: int) -> bool:
	# Check if a user is banned from using a module
	banned_modules = await mph.access_control.get_banned_modules(user, guild)
	return module in banned_modules
