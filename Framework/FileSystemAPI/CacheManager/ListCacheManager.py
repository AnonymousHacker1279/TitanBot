from Framework.FileSystemAPI.CacheManager.DatabaseCacheManager import DatabaseCacheManager


class ListCacheManager(DatabaseCacheManager):

	def __init__(self, path_to_database: str, cache_name: str, guild_id: int, management_portal_handler=None):
		super().__init__(path_to_database, cache_name, guild_id, management_portal_handler, "ListCacheManager")

	async def add_to_list_cache(self, new_object: list) -> None:
		"""Add a new list object to the cache."""
		self.cache.append(new_object)

	async def remove_from_list_cache(self, removed_object: list) -> None:
		"""Remove a list object from the cache."""
		self.cache.remove(removed_object)
