import json
import os

from Framework.FileSystemAPI import DefaultDatabaseSchemas
from Framework.FileSystemAPI.DataMigration.DataMigrator import migrate_storage_metadata


async def prepare_to_get_database_object(directory_path: str, object_path: str, default_database_schema=None,
										is_directory: bool = False) -> None:
	if default_database_schema is None:
		default_database_schema = {}
	if is_directory and not await does_directory_exist(object_path):
		os.makedirs(object_path)
		return
	if not directory_path == "" and not await does_directory_exist(directory_path):
		os.makedirs(directory_path)
	if not is_directory and not await does_file_exist(object_path):
		await create_default_database_from_schema(object_path, default_database_schema)


async def does_directory_exist(directory: str) -> bool:
	return os.path.isdir(directory)


async def does_file_exist(file: str) -> bool:
	return os.path.isfile(file)


async def create_default_database_from_schema(file: str, default_schema: dict) -> None:
	with open(file, "w") as f:
		json.dump(default_schema, f, indent=4)


async def create_empty_file(file: str) -> None:
	with open(file, "w") as f:
		f.write("")


async def check_storage_metadata(current_database_version: int, guilds) -> None:
	object_path = os.path.abspath(
			os.getcwd() + "/Storage/GuildStorageMetadata.json")
	directory_path = os.path.dirname(object_path)

	await prepare_to_get_database_object(directory_path, object_path,
										await DefaultDatabaseSchemas.get_storage_metadata_schema())

	with open(object_path, "r") as f:
		metadata = json.load(f)

	# Check if the metadata contains all the guilds
	for guild in guilds:
		# Check if data needs to be migrated from an older version
		if metadata["guilds"][str(guild.id)] < current_database_version:
			await migrate_storage_metadata(str(guild.id), metadata["guilds"][str(guild.id)])

		if str(guild.id) not in metadata["guilds"]:
			metadata["guilds"][str(guild.id)] = current_database_version

	with open(object_path, "r") as f:
		metadata = json.load(f)
	with open(object_path, "w") as f:
		json.dump(metadata, f, indent=4)
