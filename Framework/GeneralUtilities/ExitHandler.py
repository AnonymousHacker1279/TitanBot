from Framework.FileSystemAPI.CacheManager import DatabaseCacheManager


async def prepare_to_exit():
	# Sync all database caches to disk
	for instance in DatabaseCacheManager.instances:
		await instance.sync_cache_to_disk()
