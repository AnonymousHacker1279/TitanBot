import os

from dotenv import load_dotenv

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues, BotStatus


async def update_bot_status(mph):
	# Update the bot status
	status_config = await mph.cm.get_value("discord_status")
	status = await BotStatus.get_status(status_config["activity_level"], status_config["activity_text"],
										status_config["activity_url"], status_config["activity_emoji"],
										status_config["status_level"])
	await mph.bot.change_presence(activity=status[0], status=status[1])


class ConfigurationManager:

	def __init__(self):
		self.is_legacy = False
		self.global_config = {}
		self.bot_config = {}

	async def load_core_config(self):
		# Core data will always remain in a .env file in the root directory of the project
		# This data consists of the bot token and management portal information
		load_dotenv()
		self.bot_config["bot_token"] = os.getenv("DISCORD_TOKEN")
		self.bot_config["management_portal_url"] = os.getenv("MANAGEMENT_PORTAL_URL")

		ConfigurationValues.TOKEN = self.bot_config["bot_token"]
		ConfigurationValues.MANAGEMENT_PORTAL_URL = self.bot_config["management_portal_url"]

	async def load_deferred_configs(self, mph, guilds):
		self.global_config = await mph.get_management_portal_configuration("global")

		self.bot_config["discord_status"] = self.global_config["discord_status"]
		self.bot_config["superuser_list"] = self.global_config["superuser_configuration"]["superuser_list"]
		self.bot_config["bot_update"] = self.global_config["bot_update"]
		self.bot_config["log_level"] = self.global_config["logging"]["logging_level"]
		self.bot_config["genius_api_token"] = self.global_config["genius_music"]["genius_api_key"]
		self.bot_config["cf_api_token"] = self.global_config["curseforge"]["cf_api_key"]

		for guild in guilds:
			server_config = await mph.get_management_portal_configuration(guild.id)

			self.bot_config[guild.id] = {}
			self.bot_config[guild.id]["enable_logging"] = await self.__get_server_specific_config_value(server_config, "logging", "enable_logging")
			self.bot_config[guild.id]["enabled_modules"] = server_config["enabled_modules"]

		await self.update_configuration_constants(mph)
		await update_bot_status(mph)

	async def __get_server_specific_config_value(self, server_config: dict, *sections):
		"""
		Used while populating deferred configs. If a KeyError is thrown, check the global config.
		"""
		try:
			for section in sections:
				server_config = server_config[section]
			return server_config
		except KeyError:
			global_config = self.global_config
			for section in sections:
				global_config = global_config[section]
			return global_config

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

	async def get_guild_specific_value(self, guild_id, key):
		return self.bot_config[guild_id][key]

	async def get_value(self, key):
		return self.bot_config[key]
