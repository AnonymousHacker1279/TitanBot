import datetime
import json
import os

from Framework.FileSystemAPI import DatabaseObjects
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.GeneralUtilities import GeneralUtilities
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


class DataMigrator:

	def __init__(self, management_portal_handler: ManagementPortalHandler):
		self.logger = ThreadedLogger("DataMigrator", management_portal_handler)
		self.mp = management_portal_handler

	async def migrate_storage_metadata(self, guild: str, old_version: int) -> None:
		metadata_path = os.path.abspath(
				os.getcwd() + "/Storage/GuildStorageMetadata.json")

		with open(metadata_path, "r") as metadata_file:
			metadata = json.load(metadata_file)

		# Migrate from version 1 to version 2
		if old_version == 1:
			self.logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 1 to version 2")
			old_version = 2
			# Version 2 renamed the custom commands metadata file
			metadata["guilds"][guild] = 2
			object_path = os.path.abspath(os.getcwd() + "/Storage/{}/CustomCommands/metadata.json".format(str(guild)))
			os.renames(object_path, object_path.replace("metadata.json", "CommandsMetadata.json"))

		# Migrate from version 2 to version 3
		if old_version == 2:
			self.logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 2 to version 3")
			old_version = 3
			# Version 3 changed the author key in the quotes file to use ints instead of strings
			metadata["guilds"][guild] = 3

			with open(await DatabaseObjects.get_quotes_database(int(guild)), "r") as quotes_file:
				quotes = json.load(quotes_file)

			for quote in quotes:
				try:
					quote["author"] = int(await GeneralUtilities.strip_usernames(str(quote["author"])))
				except ValueError:
					pass

			with open(await DatabaseObjects.get_quotes_database(int(guild)), "w") as quotes_file:
				json.dump(quotes, quotes_file, indent=4)

		# Migrate from version 3 to version 4
		if old_version == 3:
			self.logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 3 to version 4")
			old_version = 4
			# Version 4 added a date field and a "quoted_by" field. Old entries will have the missing fields
			# set with a value of "Unknown"
			metadata["guilds"][guild] = 4

			with open(await DatabaseObjects.get_quotes_database(int(guild)), "r") as quotes_file:
				quotes = json.load(quotes_file)

			for quote in quotes:
				try:
					quote["date"] = "Unknown"
					quote["quoted_by"] = "Unknown"
				except ValueError:
					pass

			with open(await DatabaseObjects.get_quotes_database(int(guild)), "w") as quotes_file:
				json.dump(quotes, quotes_file, indent=4)

		# Migrate from version 4 to version 5
		if old_version == 4:
			self.logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 4 to version 5")
			old_version = 5
			# Version 5 removed the Modules.json file
			metadata["guilds"][guild] = 5

			object_path = os.path.abspath(os.getcwd() + "/Storage/{}/Settings/Modules.json".format(str(guild)))
			os.remove(object_path)

		# Migrate from version 5 to version 6
		if old_version == 5:
			self.logger.log_info("Migrating guild storage metadata for guild " + guild + " from version 5 to version 6")
			old_version = 6
			# Version 6 migrates all JSON storages to a MySQL database hosted on its management portal
			metadata["guilds"][guild] = 6

			# Migrate the quotes database
			with open(await DatabaseObjects.get_quotes_database(int(guild)), "r") as quotes_file:
				json_data = json.load(quotes_file)

				# Replace all "Unknown" date values with an empty timestamp
				for quote in json_data:
					if quote["date"] == "Unknown":
						quote["date"] = datetime.datetime(1970, 1, 1, 0, 0, 0).isoformat()

				# Replace all "Unknown" quoted_by values with an empty ID
				for quote in json_data:
					if quote["quoted_by"] == "Unknown":
						quote["quoted_by"] = 0

				# Check the author IDs and ensure it is a valid integer
				delete_list = []
				for quote in json_data:
					try:
						quote["author"] = int(quote["author"])
					except ValueError:
						# The quote will be deleted
						# Store deleted quotes in a separate file as a backup
						delete_list.append(quote)
						json_data.remove(quote)

				if len(delete_list) > 0:
					# Dump the deleted quotes to a file
					backup_file_name = "DeletedQuotesBackup_{}.json".format(guild)
					with open(await DatabaseObjects.get_backup_directory() + "\\" + backup_file_name, "w") as backup_file:
						json.dump(delete_list, backup_file, indent=4)

					self.logger.log_warning("Deleted {} quotes from guild {} due to invalid author IDs".format(len(delete_list), guild))

				data = json.dumps(json_data)
				await self.mp.data_migration.migrate_quotes(int(guild), data)

			# Delete the old quotes database
			os.remove(await DatabaseObjects.get_quotes_database(int(guild)))

		with open(metadata_path, "w") as metadata_file:
			json.dump(metadata, metadata_file, indent=4)
