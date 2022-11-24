import json
import os

from Framework.FileSystemAPI import DatabaseObjects
from Framework.GeneralUtilities import GeneralUtilities

logger = None


def initialize(management_portal_handler=None):
	global logger

	from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
	logger = ThreadedLogger("DataMigrator", management_portal_handler)


async def migrate_storage_metadata(guild: str, old_version: int) -> None:
	metadata_path = os.path.abspath(
			os.getcwd() + "/Storage/GuildStorageMetadata.json")

	with open(metadata_path, "r") as f:
		metadata = json.load(f)

	# Migrate from version 1 to version 2
	if old_version == 1:
		logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 1 to version 2")
		old_version = 2
		# Version 2 renamed the custom commands metadata file
		metadata["guilds"][guild] = 2
		object_path = os.path.abspath(os.getcwd() + "/Storage/{}/CustomCommands/metadata.json".format(str(guild)))
		os.renames(object_path, object_path.replace("metadata.json", "CommandsMetadata.json"))

		with open(metadata_path, "w") as f:
			json.dump(metadata, f, indent=4)

	# Migrate from version 2 to version 3
	if old_version == 2:
		logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 2 to version 3")
		old_version = 3
		# Version 3 changed the author key in the quotes file to use ints instead of strings
		metadata["guilds"][guild] = 3

		with open(await DatabaseObjects.get_quotes_database(int(guild)), "r") as f:
			quotes = json.load(f)

		for quote in quotes:
			try:
				quote["author"] = int(await GeneralUtilities.strip_usernames(str(quote["author"])))
			except ValueError:
				pass

		with open(await DatabaseObjects.get_quotes_database(int(guild)), "w") as f:
			json.dump(quotes, f, indent=4)

		with open(metadata_path, "w") as f:
			json.dump(metadata, f)

	# Migrate from version 3 to version 4
	if old_version == 3:
		logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 3 to version 4")
		old_version = 4
		# Version 4 added a date field and a "quoted_by" field. Old entries will have the missing fields
		# set with a value of "Unknown"
		metadata["guilds"][guild] = 4

		with open(await DatabaseObjects.get_quotes_database(int(guild)), "r") as f:
			quotes = json.load(f)

		for quote in quotes:
			try:
				quote["date"] = "Unknown"
				quote["quoted_by"] = "Unknown"
			except ValueError:
				pass

		with open(await DatabaseObjects.get_quotes_database(int(guild)), "w") as f:
			json.dump(quotes, f, indent=4)

		with open(metadata_path, "w") as f:
			json.dump(metadata, f)

	# Migrate from version 4 to version 5
	if old_version == 4:
		logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 4 to version 5")
		old_version = 5
		# Version 5 removed the Modules.json file
		metadata["guilds"][guild] = 5

		object_path = os.path.abspath(os.getcwd() + "/Storage/{}/Settings/Modules.json".format(str(guild)))
		os.remove(object_path)

		with open(metadata_path, "w") as f:
			json.dump(metadata, f)
