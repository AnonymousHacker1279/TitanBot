import json
import os

from Framework.FileSystemAPI import DatabaseObjects
from Framework.GeneralUtilities import GeneralUtilities


async def migrate_storage_metadata(old_version: int) -> None:
	metadata_path = os.path.abspath(
			os.getcwd() + "/Storage/GuildStorageMetadata.json")

	with open(metadata_path, "r") as f:
		metadata = json.load(f)

	# Migrate from version 1 to version 2
	if old_version == 1:
		# Version 2 renamed the custom commands metadata file
		for guild in metadata["guilds"]:
			metadata["guilds"][guild] = 2
			object_path = os.path.abspath(os.getcwd() + "/Storage/{}/CustomCommands/metadata.json".format(str(guild)))
			os.renames(object_path, object_path.replace("metadata.json", "CommandsMetadata.json"))

		with open(metadata_path, "w") as f:
			json.dump(metadata, f, indent=4)

	# Migrate from version 2 to version 3
	if old_version == 2:
		# Version 3 changed the author key in the quotes file to use ints instead of strings
		for guild in metadata["guilds"]:
			metadata["guilds"][guild] = 3

			with open(await DatabaseObjects.get_quotes_database(guild), "r") as f:
				quotes = json.load(f)

			for quote in quotes:
				try:
					quote["author"] = int(await GeneralUtilities.strip_usernames(str(quote["author"])))
				except ValueError:
					pass

			with open(await DatabaseObjects.get_quotes_database(guild), "w") as f:
				json.dump(quotes, f, indent=4)

		with open(metadata_path, "w") as f:
			json.dump(metadata, f)

	# Migrate from version 3 to version 4
	if old_version == 3:
		# Version 4 added a date field and a "quoted_by" field. Old entries will have the missing fields
		# set with a value of "Unknown"
		for guild in metadata["guilds"]:
			metadata["guilds"][guild] = 4

			with open(await DatabaseObjects.get_quotes_database(guild), "r") as f:
				quotes = json.load(f)

			for quote in quotes:
				try:
					quote["date"] = "Unknown"
					quote["quoted_by"] = "Unknown"
				except ValueError:
					pass

			with open(await DatabaseObjects.get_quotes_database(guild), "w") as f:
				json.dump(quotes, f, indent=4)

		with open(metadata_path, "w") as f:
			json.dump(metadata, f)
