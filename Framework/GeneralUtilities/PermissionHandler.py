import discord

from Framework.GeneralUtilities import CommandAccess


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
	if await CommandAccess.is_superuser(mph, ctx.author.id):
		return embed, failedPermissionCheck

	if shouldCheckForModuleEnabled and not await CommandAccess.check_module_enabled(mph, module, guild_id):
		embed.title = "Cannot use this module"
		embed.description = "This module has been disabled."
		failedPermissionCheck = True
	elif shouldCheckForBannedModule and await CommandAccess.check_user_is_banned_from_module(mph, ctx.author.id, module, guild_id):
		embed.title = "Cannot use this module"
		embed.description = "You do not have access to use this module."
		failedPermissionCheck = True
	elif shouldCheckForBannedCommand and await CommandAccess.check_user_is_banned_from_command(mph, ctx.author.id, command, guild_id):
		embed.title = "Cannot use this command"
		embed.description = "You do not have permission to use this command."
		failedPermissionCheck = True
	elif shouldCheckForAdmin and not ctx.author.guild_permissions.administrator:
		embed.title = "Cannot use this command"
		embed.description = "You do not have access to use this command."
		failedPermissionCheck = True

	return embed, failedPermissionCheck
