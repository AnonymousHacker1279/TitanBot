import json

from Framework.GeneralUtilities import GeneralUtilities


class DatabaseCacheManager:

	def __init__(self, path_to_database):
		self.cache = {}
		self.path_to_database = path_to_database

		GeneralUtilities.run_and_get(self.__load_database())

	async def __load_database(self) -> None:
		"""Load the database into the cache."""
		with open(self.path_to_database, 'r') as f:
			self.cache = json.load(f)

	async def __save_database(self) -> None:
		"""Save the cache to the database."""
		with open(self.path_to_database, 'w') as f:
			json.dump(self.cache, f, indent=4)

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
		await self.__load_database()
