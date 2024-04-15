import json
import os

from dotenv import load_dotenv

from Framework.ConfigurationManager import ConfigurationValues, BotStatus
from Framework.ManagementPortal.APIEndpoints import APIEndpoints


class ConfigurationManager:

	def __init__(self):
		self.__global_config = {}
		self.__bot_config = {}
		self.mph = None

	def load_core_config(self):
		# Core data will always remain in a .env file in the root directory of the project
		# This data consists of the bot token and management portal information
		load_dotenv()
		self.__bot_config["bot_token"] = os.getenv("DISCORD_TOKEN")
		self.__bot_config["management_portal_url"] = os.getenv("MANAGEMENT_PORTAL_URL")
		self.__bot_config["ipc_address"] = os.getenv("IPC_ADDRESS")
		self.__bot_config["ipc_port"] = int(os.getenv("IPC_PORT"))

		ConfigurationValues.TOKEN = self.__bot_config["bot_token"]
		ConfigurationValues.MANAGEMENT_PORTAL_URL = self.__bot_config["management_portal_url"]
		ConfigurationValues.IPC_ADDRESS = self.__bot_config["ipc_address"]
		ConfigurationValues.IPC_PORT = self.__bot_config["ipc_port"]

	async def load_deferred_configs(self, guilds):
		from Framework.ManagementPortal import management_portal_handler
		self.mph = management_portal_handler

		self.__global_config = await self.__pull_configuration("global")

		self.__bot_config["discord_status"] = self.__global_config["discord_status"]

		self.__bot_config["superuser_configuration"] = {}
		self.__bot_config["superuser_configuration"]["superuser_list"] = self.__global_config["superuser_configuration"]["superuser_list"]

		self.__bot_config["bot_update"] = self.__global_config["bot_update"]

		self.__bot_config["logging"] = {}
		self.__bot_config["logging"]["enable_logging"] = self.__global_config["logging"]["enable_logging"]
		self.__bot_config["logging"]["logging_level"] = self.__global_config["logging"]["logging_level"]

		self.__bot_config["genius_music"] = {}
		self.__bot_config["genius_music"]["genius_api_key"] = self.__global_config["genius_music"]["genius_api_key"]

		self.__bot_config["curseforge"] = {}
		self.__bot_config["curseforge"]["cf_api_key"] = self.__global_config["curseforge"]["cf_api_key"]

		self.__bot_config["enabled_modules"] = self.__global_config["enabled_modules"]

		for guild in guilds:
			server_config = await self.__pull_configuration(str(guild.id))

			self.__bot_config[guild.id] = {}
			self.__bot_config[guild.id]["enabled_modules"] = server_config["enabled_modules"]

		await self.update_configuration_constants()
		await self.update_bot_status()

	async def __get_server_specific_config_value(self, server_config: dict, *sections):
		"""
		Used while populating deferred configs. If a KeyError is thrown, check the global config.
		"""
		try:
			for section in sections:
				server_config = server_config[section]
			return server_config
		except KeyError:
			global_config = self.__global_config
			for section in sections:
				global_config = global_config[section]
			return global_config

	async def __pull_configuration(self, file_name: str) -> dict:
		"""Get a configuration from the management portal."""
		data = self.mph.base_data.copy()
		data["name"] = file_name
		return await self.mph.get(APIEndpoints.GET_CONFIGURATION, data)

	async def __push_configuration(self, file_name: str, config: dict) -> None:
		"""Push a configuration to the management portal."""
		data = self.mph.base_data.copy()
		data["name"] = file_name
		data["config"] = json.dumps(config)
		await self.mph.post(APIEndpoints.WRITE_CONFIGURATION, data)

	async def update_bot_status(self):
		# Update the bot status
		status_config = await self.get_value("discord_status")
		status = await BotStatus.get_status(status_config["activity_level"], status_config["activity_text"],
											status_config["activity_url"], status_config["activity_emoji"],
											status_config["status_level"])
		await self.mph.bot.change_presence(activity=status[0], status=status[1])

	async def update_configuration_constants(self):
		ConfigurationValues.LOG_LEVEL = await self.get_value("logging/logging_level")

		bot_update = await self.get_value("bot_update")
		ConfigurationValues.AUTO_UPDATE_ENABLED = bot_update["enable_updates"]
		ConfigurationValues.UPDATE_REPOSITORY = bot_update["update_repository"]
		ConfigurationValues.UPDATE_BRANCH = bot_update["update_branch"]
		ConfigurationValues.UPDATE_CHECK_FREQUENCY = bot_update["update_check_frequency"]

		ConfigurationValues.GENIUS_API_TOKEN = await self.get_value("genius_music/genius_api_key")
		ConfigurationValues.CF_API_TOKEN = await self.get_value("curseforge/cf_api_key")

	async def get_guild_specific_value(self, guild_id, key) -> any:
		return self.__bot_config[guild_id][key]

	async def get_value(self, key) -> any:
		"""Get a value from the bot configuration. Entry may be nested by using slashes."""
		if "/" in key:
			keys = key.split("/")
			config = self.__bot_config
			for k in keys:
				config = config[k]
			return config
		else:
			return self.__bot_config[key]

	async def get_config(self) -> dict:
		return self.__bot_config

	async def set_value(self, key: str, value, update_mp=False) -> None:
		"""
		Set a value in the bot configuration. Note this does not propagate to the management portal by default.
		:param key: The key to set. May be nested by using slashes.
		:param value: The value to set
		:param update_mp: Whether to update the management portal. Note that core values provided through the .env file will not be updated in the management portal regardless of this setting.
		"""

		# Check for nested entries
		if "/" in key:
			keys = key.split("/")
			config = self.__bot_config
			for k in keys[:-1]:
				config = config[k]
			config[keys[-1]] = value
		else:
			self.__bot_config[key] = value

		disallowed_keys = ["bot_token", "management_portal_url", "ipc_address", "ipc_port"]
		if update_mp and key not in disallowed_keys:
			# Determine if the key was global or server-specific. A root-level entry that's a number should be tested to see if it is a guild ID
			if key.isnumeric() and self.mph.bot.get_guild(int(key)) is not None:
				await self.__push_configuration(key, self.__bot_config[key])
			else:
				# Strip all server-specific keys by removing all numeric keys
				global_config = self.__bot_config.copy()
				for k in global_config.keys():
					try:
						int(k)
						disallowed_keys.append(k)
					except ValueError:
						pass

				for k in disallowed_keys:
					global_config.pop(k)

				await self.__push_configuration("global", global_config)

		await self.update_configuration_constants()
		await self.update_bot_status()
