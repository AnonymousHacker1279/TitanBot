from discord import utils
from discord.ext import commands

from . import Constants, GeneralUtilities
from ..FileSystemAPI import DatabaseObjects
from ..FileSystemAPI.CacheManager.DatabaseCacheManager import DatabaseCacheManager
from ..FileSystemAPI.CacheManager.ListCacheManager import ListCacheManager

cache_managers = {}


async def post_initialize(bot: commands.Bot):
	for guild in bot.guilds:
		cache_managers["module_settings"] = {}
		cache_managers["module_settings"][guild.id] = \
			DatabaseCacheManager(await DatabaseObjects.get_module_settings_database(guild.id))

		cache_managers["revoked_commands"] = {}
		cache_managers["revoked_commands"][guild.id] = \
			ListCacheManager(await DatabaseObjects.get_revoked_commands_database(guild.id))

		cache_managers["revoked_modules"] = {}
		cache_managers["revoked_modules"][guild.id] = \
			ListCacheManager(await DatabaseObjects.get_revoked_modules_database(guild.id))


async def check_module_enabled(module: str, guild: int):
	# Open the settings file
	data = await cache_managers["module_settings"].get(guild).get_cache()

	# Get status
	return data["moduleConfiguration"][module]["enabled"]


async def check_user_is_banned_from_command(user: str, command: str, guild: int):
	# Check if a user is banned from using a command
	data = await cache_managers["revoked_commands"].get(guild).get_cache()

	# Check if the user is banned from using the command
	maxIndex = 0
	user = await GeneralUtilities.strip_usernames(user)
	for _ in data:
		if user in data[maxIndex]["user"] and command in data[maxIndex]["revokedCommands"]:
			return True
		maxIndex = maxIndex + 1
	return False


async def check_user_is_banned_from_module(user: str, module: str, guild: int):
	# Check if a user is banned from using a module
	data = await cache_managers["revoked_modules"].get(guild).get_cache()

	# Check if the user is banned from using the module
	maxIndex = 0
	user = await GeneralUtilities.strip_usernames(user)
	for _ in data:
		if user in data[maxIndex]["user"] and module in data[maxIndex]["revokedModules"]:
			return True
		maxIndex = maxIndex + 1
	return False
