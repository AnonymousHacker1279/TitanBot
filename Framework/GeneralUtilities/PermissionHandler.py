import discord

from Framework.ConfigurationManager import configuration_manager as cm
from Framework.ManagementPortal import management_portal_handler as mph


async def check_permissions(ctx, embed: discord.Embed, module: str, command: str, should_check_for_admin=False) -> tuple[discord.Embed, bool]:
	"""
	Check if the user has permission to use a command. The check process is as follows:

	1. Check if the user is a superuser. If so, they will always have access.
	2. Check if the module is enabled. This is global for an entire guild.
	3. Check if the user is banned from using the module.
	4. Check if the user is banned from using the command.
	5. Check if the user is an administrator (if the command requires it).

	If any of these checks fail, the embed will be updated with the appropriate message and the calling command should exit early.

	:param ctx: The context of the command.
	:param embed: The embed to update if the permission check fails.
	:param module: The module the command belongs to.
	:param command: The command being executed.
	:param should_check_for_admin: Whether the command requires administrator permissions.
	"""

	failed_permission_check = False
	guild_id = ctx.guild.id

	if await is_superuser(ctx.author.id):
		return embed, failed_permission_check

	if not await check_module_enabled(module, guild_id):
		embed.title = "Cannot use this module"
		embed.description = "This module has been disabled."
		failed_permission_check = True
	elif await check_user_is_banned_from_module(ctx.author.id, module, guild_id):
		embed.title = "Cannot use this module"
		embed.description = "You do not have access to use this module."
		failed_permission_check = True
	elif await check_user_is_banned_from_command(ctx.author.id, module, command, guild_id):
		embed.title = "Cannot use this command"
		embed.description = "You do not have permission to use this command."
		failed_permission_check = True
	elif should_check_for_admin and not ctx.author.guild_permissions.administrator:
		embed.title = "Cannot use this command"
		embed.description = "You do not have access to use this command."
		failed_permission_check = True

	return embed, failed_permission_check


async def is_superuser(user: int) -> bool:
	superusers = await cm.get_value("superuser_configuration/superuser_list")
	return str(user) in superusers


async def check_module_enabled(module: str, guild: int) -> bool:
	enabled_modules = await cm.get_guild_specific_value(guild, "enabled_modules")
	return enabled_modules[module + "_enabled"]


async def check_user_is_banned_from_command(user: int, module: str, command: str, guild: int) -> bool:
	banned_commands = await mph.access_control_api.get_banned_commands(user, guild)
	return (command + "[" + module + "]") in banned_commands


async def check_user_is_banned_from_module(user: int, module: str, guild: int) -> bool:
	banned_modules = await mph.access_control_api.get_banned_modules(user, guild)
	return module in banned_modules
