import json

from Framework.FileSystemAPI.Logger import Logger
from Framework.GeneralUtilities import GeneralUtilities


class DatabaseCacheManager:

	def __init__(self, path_to_database: str, cache_name: str, guild_id: int, management_portal_handler,
				logger_name: str = "DatabaseCacheManager"):
		self.cache = {}
		self.path_to_database = path_to_database
		self.cache_name = cache_name
		self.guild_id = str(guild_id)
		self.logger = Logger(logger_name, management_portal_handler)

		GeneralUtilities.run_and_get(self.__load_database())

	async def __load_database(self) -> None:
		"""Load the database into the cache."""
		with open(self.path_to_database, 'r') as f:
			self.cache = json.load(f)

		await self.logger.log_debug("(Cache: " + self.cache_name + ", guild: " + self.guild_id + ") " +
									"Loaded database from disk into cache")
		await self.logger.log_debug("(Cache: " + self.cache_name + ", guild: " + self.guild_id + ") " +
									"Cache objects loaded: " + str(len(self.cache)))

	async def __save_database(self) -> None:
		"""Save the cache to the database."""
		with open(self.path_to_database, 'w') as f:
			json.dump(self.cache, f, indent=4)

		await self.logger.log_debug("(Cache: " + self.cache_name + ", guild: " + self.guild_id + ") " +
									"Saved database from cache to disk")
		await self.logger.log_debug("(Cache: " + self.cache_name + ", guild: " + self.guild_id + ") " +
									"Cache objects saved: " + str(len(self.cache)))

	async def get_cache(self) -> dict:
		"""Get the cache object held by this manager."""
		return self.cache

	async def add_to_cache(self, key, value) -> None:
		"""Add a new key-value pair to the cache."""
		self.cache[key] = value

	async def remove_from_cache(self, key) -> None:
		"""Remove a key-value pair from the cache."""
		self.cache.pop(key)

	async def sync_cache_to_disk(self) -> None:
		"""Sync the cache to the disk."""
		await self.__save_database()

	async def invalidate_cache(self) -> None:
		"""Invalidate the cache, forcing it to be reloaded from disk."""
		await self.logger.log_debug("(Cache: " + self.cache_name + ", guild: " + self.guild_id + ") "
								+ "Invalidating cache with size: " + str(len(self.cache)))
		await self.__load_database()
