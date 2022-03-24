import json

from discord import utils

from . import Constants
from ..GeneralUtilities import GeneralUtilities as Utilities


async def check_module_enabled(module: str):
	# Open the settings file
	with open(await Utilities.get_module_settings_database(), 'r') as f:
		data = json.load(f)

	# Get status
	return data["moduleConfiguration"][module]["enabled"]


async def check_user_is_wizard(ctx):
	# Check if a user is a wizard
	# The "wizard" check ensures that a user has permissions
	#  to use moderator-level commands.
	return utils.get(ctx.author.roles, id=Constants.WIZARD_ROLE)


async def check_user_is_banned_from_command(user: str, command: str):
	# Check if a user is banned from using a command
	with open(await Utilities.get_revoked_commands_database(), 'r') as f:
		data = json.load(f)

	# Check if the user is banned from using the command
	maxIndex = 0
	user = user.lstrip("<@!").rstrip(">")
	for _ in data:
		if user in data[maxIndex]["user"] and command in data[maxIndex]["revokedCommands"]:
			return True
		maxIndex = maxIndex + 1
	return False


async def check_user_is_banned_from_module(user: str, module: str):
	# Check if a user is banned from using a module
	with open(await Utilities.get_revoked_modules_database(), 'r') as f:
		data = json.load(f)

	# Check if the user is banned from using the module
	maxIndex = 0
	user = user.lstrip("<@!").rstrip(">")
	for _ in data:
		if user in data[maxIndex]["user"] and module in data[maxIndex]["revokedModules"]:
			return True
		maxIndex = maxIndex + 1
	return False
