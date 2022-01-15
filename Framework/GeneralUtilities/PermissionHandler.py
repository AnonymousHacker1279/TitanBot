from Framework.GeneralUtilities import CommandAccess


async def check_permissions(ctx, embed, module, command, shouldCheckForWizard=False, shouldCheckForModuleEnabled=True,
							shouldCheckForBannedModule=True, shouldCheckForBannedCommand=True):
	failedPermissionCheck = False
	if shouldCheckForModuleEnabled and not await CommandAccess.check_module_enabled(module):
		embed.title = "Cannot use this module"
		embed.description = "This module has been disabled."
		failedPermissionCheck = True
	elif shouldCheckForBannedModule and await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, module):
		embed.title = "Cannot use this module"
		embed.description = "You do not have access to use this module."
		failedPermissionCheck = True
	elif shouldCheckForBannedCommand and await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, command):
		embed.title = "Cannot use this command"
		embed.description = "You do not have permission to use this command."
		failedPermissionCheck = True
	elif shouldCheckForWizard and await CommandAccess.check_user_is_wizard(ctx) is None:
		embed.title = "Cannot use this command"
		embed.description = "You do not have access to use this command."
		failedPermissionCheck = True

	return embed, failedPermissionCheck
