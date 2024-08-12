import discord

from Framework.ConfigurationManager import configuration_manager as cm


async def check_permissions(ctx, embed: discord.Embed, module: str) -> tuple[discord.Embed, bool]:
	"""
	Check if the user has permission to use a command. The check process is as follows:

	1. Check if the user is a superuser. If so, they will always have access.
	2. Check if the module is enabled. This is global for an entire guild.

	If any of these checks fail, the embed will be updated with the appropriate message and the calling command should exit early.
	Discord now supports enabling/disabling commands on a per-user/role basis, so that ability has been removed from this function.

	:param ctx: The context of the command.
	:param embed: The embed to update if the permission check fails.
	:param module: The module the command belongs to.
	"""

	failed_permission_check = False
	guild_id = ctx.guild.id

	if await is_superuser(ctx.author.id):
		return embed, failed_permission_check

	if not await check_module_enabled(module, guild_id):
		embed.title = "Cannot use this module"
		embed.description = "This module has been disabled."
		failed_permission_check = True

	return embed, failed_permission_check


async def is_superuser(user: int) -> bool:
	superusers = await cm.get_value("superuser_configuration/superuser_list")
	return user in superusers


async def check_module_enabled(module: str, guild: int) -> bool:
	global_enabled_modules = await cm.get_value("enabled_modules")
	guild_enabled_modules = await cm.get_guild_specific_value(guild, "enabled_modules")
	return module in global_enabled_modules and module in guild_enabled_modules
