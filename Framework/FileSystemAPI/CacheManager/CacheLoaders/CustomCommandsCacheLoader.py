import os

from Framework.FileSystemAPI import DatabaseObjects
from Framework.FileSystemAPI.CacheManager import DatabaseCacheManager


class CacheLoader:

	def __init__(self):
		pass

	async def load_data_cache(self, cache_manager: DatabaseCacheManager, guild_id: int):
		# Load custom commands from file into cache
		# Find all files ending in .js in the custom_commands directory
		custom_commands_directory = await DatabaseObjects.get_custom_commands_directory(guild_id)
		for file in os.listdir(custom_commands_directory):
			if file.endswith(".js"):
				# Load the file into the cache
				with open(os.path.join(custom_commands_directory, file), "r") as f:
					command = f.read()
					# Get the file name without extension
					command_name = os.path.splitext(file)[0]
					await cache_manager.add_to_cache(command_name, command)
