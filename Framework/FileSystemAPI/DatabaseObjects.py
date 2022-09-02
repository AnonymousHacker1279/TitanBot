import os

from Framework.FileSystemAPI import DefaultDatabaseSchemas, FileAPI


async def get_module_settings_database(guild: int = None) -> str:
	object_path = os.path.abspath(os.getcwd() + "/Storage/{}/Settings/Modules.json".format(str(guild)))
	directory_path = os.path.dirname(object_path)

	await FileAPI.prepare_to_get_database_object(directory_path, object_path, await DefaultDatabaseSchemas.get_modules_schema())

	return object_path


async def get_quotes_database(guild: int = None) -> str:
	object_path = os.path.abspath(os.getcwd() + "/Storage/{}/Quotes.json".format(str(guild)))
	directory_path = os.path.dirname(object_path)

	await FileAPI.prepare_to_get_database_object(directory_path, object_path, await DefaultDatabaseSchemas.get_empty_schema())
	return object_path


async def get_revoked_commands_database(guild: int = None) -> str:
	object_path = os.path.abspath(os.getcwd() + "/Storage/{}/Settings/UserAccess/Commands/RevokedCommands.json".format(str(guild)))
	directory_path = os.path.dirname(object_path)

	await FileAPI.prepare_to_get_database_object(directory_path, object_path, await DefaultDatabaseSchemas.get_empty_schema())
	return object_path


async def get_revoked_modules_database(guild: int = None) -> str:
	object_path = os.path.abspath(os.getcwd() + "/Storage/{}/Settings/UserAccess/Modules/RevokedModules.json".format(str(guild)))
	directory_path = os.path.dirname(object_path)

	await FileAPI.prepare_to_get_database_object(directory_path, object_path, await DefaultDatabaseSchemas.get_empty_schema())
	return object_path


async def get_custom_commands_directory(guild: int = None) -> str:
	object_path = os.path.abspath(os.getcwd() + "/Storage/{}/CustomCommands".format(str(guild)))

	await FileAPI.prepare_to_get_database_object("", object_path, is_directory=True)
	return object_path


async def get_custom_commands_metadata_database(guild: int = None) -> str:
	object_path = os.path.abspath(os.getcwd() + "/Storage/{}/CustomCommands/CommandsMetadata.json".format(str(guild)))
	directory_path = os.path.dirname(object_path)

	await FileAPI.prepare_to_get_database_object(directory_path, object_path, await DefaultDatabaseSchemas.get_custom_commands_metadata_schema())
	return object_path
