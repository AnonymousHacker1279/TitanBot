import discord

from Framework.ConfigurationManager import configuration_manager as cm
from Framework.ManagementPortal import management_portal_handler as mph


async def check_permissions(ctx, embed: discord.Embed,
							module: str, command: str,
							should_check_for_admin=False,
							should_check_for_module_enabled=True):

	failed_permission_check = False
	guild_id = ctx.guild.id

	if await is_superuser(ctx.author.id):
		return embed, failed_permission_check

	if should_check_for_module_enabled and not await check_module_enabled(module, guild_id):
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
