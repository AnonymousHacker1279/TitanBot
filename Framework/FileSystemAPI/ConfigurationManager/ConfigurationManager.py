import json
import os

from dotenv import load_dotenv

from Framework.FileSystemAPI import DatabaseObjects
from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues


class ConfigurationManager:

	def __init__(self):
		self.is_legacy = False
		self.bot_config = {}

	async def load_configs(self):
		await self.load_core_config()

	async def load_core_config(self):
		# Core data will always remain in a .env file in the root directory of the project
		# This data consists of the bot token and management portal information
		load_dotenv()
		self.bot_config["bot_token"] = os.getenv("DISCORD_TOKEN")
		self.bot_config["management_portal_url"] = os.getenv("MANAGEMENT_PORTAL_URL")

		ConfigurationValues.TOKEN = self.bot_config["bot_token"]
		ConfigurationValues.MANAGEMENT_PORTAL_URL = self.bot_config["management_portal_url"]

	async def load_deferred_configs(self, mph, guilds):
		for guild in guilds:
			with open(await DatabaseObjects.get_configuration_database(guild.id), "r") as config_file:
				file = json.load(config_file)

				# This data is global and should be the same in all guilds
				self.bot_config["discord_status"] = file["discord_status"]
				self.bot_config["superuser_list"] = file["superuser_configuration"]["superuser_list"]
				self.bot_config["bot_update"] = file["bot_update"]
				self.bot_config["log_level"] = file["logging"]["logging_level"]
				self.bot_config["genius_api_token"] = file["genius_music"]["genius_api_key"]
				self.bot_config["cf_api_token"] = file["curseforge"]["cf_api_key"]
				self.bot_config["virustotal_api_key"] = file["custom_commands"]["vt_api_key"]
				self.bot_config["osmium_import_whitelist"] = file["custom_commands"]["import_whitelist"]

				# This data is guild specific and could be different in each guild
				self.bot_config[guild.id] = {}
				self.bot_config[guild.id]["enable_logging"] = file["logging"]["enable_logging"]
				self.bot_config[guild.id]["enable_custom_commands_malware_scanning"] = file["custom_commands"][
					"enable_vt_scanning"]
				self.bot_config[guild.id]["custom_commands_max_execution_time"] = file["custom_commands"]["command_timeout"]
				self.bot_config[guild.id]["enabled_modules"] = file["enabled_modules"]

		await self.update_configuration_constants(mph)

	async def update_configuration_constants(self, mph):
		ConfigurationValues.LOG_LEVEL = await self.get_value("log_level")

		bot_update = await self.get_value("bot_update")
		ConfigurationValues.AUTO_UPDATE_ENABLED = bot_update["enable_updates"]
		ConfigurationValues.UPDATE_REPOSITORY = bot_update["update_repository"]
		ConfigurationValues.UPDATE_BRANCH = bot_update["update_branch"]
		ConfigurationValues.UPDATE_CHECK_FREQUENCY = bot_update["update_check_frequency"]
		mph.check_for_updates.change_interval(seconds=ConfigurationValues.UPDATE_CHECK_FREQUENCY)

		ConfigurationValues.GENIUS_API_TOKEN = await self.get_value("genius_api_token")
		ConfigurationValues.CF_API_TOKEN = await self.get_value("cf_api_token")
		ConfigurationValues.VIRUSTOTAL_API_KEY = await self.get_value("virustotal_api_key")

	async def insert_into_config(self, key, value):
		self.bot_config[key] = value

	async def get_guild_specific_value(self, guild_id, key):
		return self.bot_config[guild_id][key]

	async def get_value(self, key):
		return self.bot_config[key]
