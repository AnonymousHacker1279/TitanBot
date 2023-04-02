
async def get_custom_commands_metadata_schema() -> dict:
	return {
		"metadata": {},
		"aliases": {},
		"admin_only_commands": []
	}


async def get_storage_metadata_schema() -> dict:
	return {
		"metadata_version": 1,
		"guilds": {}
	}


async def get_empty_schema() -> list:
	return []

