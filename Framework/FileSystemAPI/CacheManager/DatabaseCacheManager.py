import json

from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.GeneralUtilities import GeneralUtilities

instances = []


class DatabaseCacheManager:

	def __init__(self, cache_name: str, guild_id: int, management_portal_handler, path_to_database: str = "",
				logger_name: str = "DatabaseCacheManager", cache_loader=None, load_with_empty_path: bool = False):
		self.cache = {}
		self.path_to_database = path_to_database
		self.cache_name = cache_name
		self.guild_id = str(guild_id)
		self.logger = ThreadedLogger(logger_name, management_portal_handler)
		self.cache_loader = cache_loader
		self.load_with_empty_path = load_with_empty_path

		# If the database path is specified, load the database into the cache
		if self.path_to_database != "":
			GeneralUtilities.run_and_get(self.__load_database())
		elif self.load_with_empty_path:
			GeneralUtilities.run_and_get(self.__load_database())

		global instances
		instances.append(self)

	async def __load_database(self) -> None:
		"""Load the database into the cache."""
		if self.cache_loader:
			await self.cache_loader.load_data_cache(self, self.guild_id)
		else:
			with open(self.path_to_database, 'r') as f:
				self.cache = json.load(f)

		self.logger.log_debug(f"(Cache: {self.cache_name}, guild: {self.guild_id}) " +
									"Loaded database from disk into cache")
		self.logger.log_debug(f"(Cache: {self.cache_name}, guild: {self.guild_id}) " +
									f"Cache objects loaded: {str(len(self.cache))}")

	async def __save_database(self) -> None:
		"""Save the cache to the database."""
		if self.path_to_database != "":
			with open(self.path_to_database, 'w') as f:
				json.dump(self.cache, f, indent=4)

			self.logger.log_debug(f"(Cache: {self.cache_name}, guild: {self.guild_id}) " +
									"Saved database from cache to disk")
			self.logger.log_debug(f"(Cache: {self.cache_name}, guild: {self.guild_id}) " +
									f"Cache objects saved: {str(len(self.cache))}")

	async def get_cache(self) -> dict:
		"""Get the cache object held by this manager."""
		return self.cache

	async def add_to_cache(self, key, value) -> None:
		"""Add a new key-value pair to the cache."""
		self.cache[key] = value

	async def remove_from_cache(self, key) -> None:
		"""Remove a key-value pair from the cache."""
		self.cache.pop(key)

	async def edit_cache(self, key, value) -> None:
		"""Edit a key-value pair in the cache."""
		self.cache[key] = value

	async def sync_cache_to_disk(self) -> None:
		"""Sync the cache to the disk."""
		await self.__save_database()

	async def invalidate_cache(self) -> None:
		"""Invalidate the cache, forcing it to be reloaded from disk."""
		self.logger.log_debug(f"(Cache: {self.cache_name}, guild: {self.guild_id}) "
								+ f"Invalidating cache with size: {str(len(self.cache))}")
		await self.__load_database()
