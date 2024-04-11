import json
import os

logger = None


def initialize():
	global logger

	from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
	logger = ThreadedLogger("FileAPI")


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
