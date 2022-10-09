from discord.ext import commands

from . import GeneralUtilities
from ..FileSystemAPI import DatabaseObjects
from ..FileSystemAPI.CacheManager.ListCacheManager import ListCacheManager

cache_managers = {}
mp = None


async def post_initialize(bot: commands.Bot, management_portal_handler):
	global mp
	mp = management_portal_handler

	cache_managers["revoked_commands"] = {}
	cache_managers["revoked_modules"] = {}

	for guild in bot.guilds:
		cache_managers["revoked_commands"][guild.id] = \
			ListCacheManager(await DatabaseObjects.get_revoked_commands_database(guild.id), "revoked_commands", guild.id, management_portal_handler)

		cache_managers["revoked_modules"][guild.id] = \
			ListCacheManager(await DatabaseObjects.get_revoked_modules_database(guild.id), "revoked_modules", guild.id, management_portal_handler)


# When the bot joins a new guild, caches need to be invalidated
async def invalidate_caches():
	for guild in cache_managers["revoked_commands"]:
		await cache_managers["revoked_commands"][guild].sync_cache_to_disk()
		await cache_managers["revoked_commands"][guild].invalidate_cache()

	for guild in cache_managers["revoked_modules"]:
		await cache_managers["revoked_modules"][guild].sync_cache_to_disk()
		await cache_managers["revoked_modules"][guild].invalidate_cache()


async def check_module_enabled(module: str, guild: int):
	enabled_modules = await mp.cm.get_guild_specific_value(guild, "enabled_modules")
	return enabled_modules[module + "_enabled"]


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
