import json
import os
from typing import Any

from discord import Guild
from dotenv import load_dotenv

from Framework.ConfigurationManager import ConfigurationValues, BotStatus


async def build_default_global_config() -> dict:
	"""
	Build a default global configuration.
	"""

	return {
		"discord_status": {
			"activity_type": 4,
			"activity_text": "",
			"activity_url": "",
			"status_type": 0
		},
		"superuser_configuration": {
			"superuser_list": []
		},
		"logging": {
			"enable_logging": True,
			"logging_level": 1
		},
		"curseforge": {
			"cf_api_key": ""
		},
		"genius": {
			"genius_api_key": ""
		},
		"enabled_modules": [
			"curseforge",
			"debugging",
			"fun",
			"genius",
			"quotes",
			"statistics",
			"utility"
		]
	}

async def build_default_guild_config() -> dict:
	"""
	Build a default guild configuration.
	"""

	return {
		"enabled_modules": [
			"curseforge",
			"debugging",
			"fun",
			"genius",
			"quotes",
			"statistics",
			"utility"
		]
	}


class ConfigurationManager:

	def __init__(self):
		self.__global_config = {}
		self.__bot_config = {}
		self.bot = None

	def load_core_config(self) -> None:
		"""Load core data that is needed very early in the loading process. These values are stored in a .env file in the root directory."""
		load_dotenv()
		self.__bot_config["bot_token"] = os.getenv("DISCORD_TOKEN")
		self.__bot_config["ipc_address"] = os.getenv("IPC_ADDRESS")
		self.__bot_config["ipc_port"] = int(os.getenv("IPC_PORT"))

		ConfigurationValues.TOKEN = self.__bot_config["bot_token"]
		ConfigurationValues.IPC_ADDRESS = self.__bot_config["ipc_address"]
		ConfigurationValues.IPC_PORT = self.__bot_config["ipc_port"]

	async def load_deferred_configs(self, guilds: list[Guild]) -> None:
		"""
		Load configuration data stored in local JSON files.

		:param guilds: The guilds the bot is currently in.
		"""

		# Open the global config file. If it doesn't exist, create it
		try:
			with open(f"{os.getcwd()}/Storage/Config/global.json", "r") as file:
				self.__global_config = json.load(file)
		except FileNotFoundError:
			self.__global_config = await build_default_global_config()
			with open(f"{os.getcwd()}/Storage/Config/global.json", "w+") as file:
				json.dump(self.__global_config, file, indent=4)

		self.__bot_config.update(self.__global_config)

		# Merge guild-specific configurations
		for guild in guilds:
			try:
				with open(f"{os.getcwd()}/Storage/Config/{guild.id}.json", "r") as file:
					server_config = json.load(file)
			except FileNotFoundError:
				server_config = await build_default_guild_config()
				with open(f"{os.getcwd()}/Storage/Config/{guild.id}.json", "w+") as file:
					json.dump(server_config, file, indent=4)

			self.__bot_config[guild.id] = {}
			self.__bot_config[guild.id]["enabled_modules"] = server_config["enabled_modules"]

		await self.update_configuration_constants()
		await self.update_bot_status()

	async def __get_server_specific_config_value(self, server_config: dict, *sections) -> Any:
		"""
		Get a server-specific config value, defaulting to the global config if nothing is found. Used specifically
		while loading deferred configs.

		:param server_config: The server-specific configuration.
		:param sections: The sections to traverse.
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

	async def update_bot_status(self) -> None:
		"""Update the bot's status based on the configuration."""
		status = await BotStatus.get_status_from_config(self)
		await self.bot.change_presence(activity=status[0], status=status[1])

	async def update_configuration_constants(self):
		"""Update the configuration constants stored in ConfigurationValues."""
		ConfigurationValues.LOG_LEVEL = await self.get_value("logging/logging_level")

	async def get_guild_specific_value(self, guild_id: int, key: str) -> Any:
		"""
		Get a value from the bot configuration that is specific to a guild. Entry may be nested by using slashes.

		:param guild_id: The ID of the guild to get the value for.
		:param key: The key to get.
		:return: The value.
		"""

		if "/" in key:
			keys = key.split("/")
			config = self.__bot_config[guild_id]
			for k in keys:
				config = config[k]
			return config
		else:
			return self.__bot_config[guild_id][key]

	async def get_value(self, key: str) -> Any:
		"""
		Get a value from the bot configuration. Entry may be nested by using slashes.

		:param key: The key to get.
		:return: The value.
		"""

		if "/" in key:
			keys = key.split("/")
			config = self.__bot_config
			for k in keys:
				config = config[k]
			return config
		else:
			return self.__bot_config[key]

	async def get_config(self) -> dict:
		"""
		Get the entire bot configuration.

		:return: The bot configuration.
		"""

		return self.__bot_config

	async def set_value(self, key: str, value: Any, update_local_config=False) -> None:
		"""
		Set a value in the bot configuration. Note this does not save to disk by default.

		:param key: The key to set. May be nested by using slashes.
		:param value: The value to set
		:param update_local_config: Whether to update the local config files. Note that core values provided through the .env file will not be updated regardless of this setting.
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

		disallowed_keys = ["bot_token", "ipc_address", "ipc_port"]
		if update_local_config and key not in disallowed_keys:
			# Determine if the key was global or server-specific. A root-level entry that's a number should be tested to see if it is a guild ID
			if key.isnumeric() and self.bot.get_guild(int(key)) is not None:
				with open(f"{os.getcwd()}/Storage/Config/{key}.json", "w+") as file:
					json.dump(self.__bot_config[key], file, indent=4)
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

				with open(f"{os.getcwd()}/Storage/Config/global.json", "w+") as file:
					json.dump(global_config, file, indent=4)

		await self.update_configuration_constants()
		await self.update_bot_status()
