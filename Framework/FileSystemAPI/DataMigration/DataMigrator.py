import json
import os


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
			json.dump(metadata, f)
