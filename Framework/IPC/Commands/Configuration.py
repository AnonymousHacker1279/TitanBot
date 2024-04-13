import json

import discord

from ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand


class Configuration(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager):
		super().__init__(bot, config_manager)
		self.friendly_name = "config"

	async def execute(self, args: list[str]) -> str:
		bot_config = await self.config_manager.get_config()

		match args[0]:
			case "get_value" | "get" | "g":
				try:
					key: str = args[1]
				except IndexError:
					return "No key provided."

				# Check for nested entries
				if "/" in key:
					keys = key.split("/")
					config = bot_config
					for k in keys:
						if k in config:
							config = config[k]
						else:
							return f"Key '{k}' not found in configuration."
					return f"{key}: {config}"

				if key in bot_config:
					return f"{key}: {bot_config[key]}"
				else:
					return f"Key '{key}' not found in configuration."

			case "dump_values" | "dump" | "d":
				try:
					pretty_print: bool = args[1] == "pretty" or args[1] == "p"
				except IndexError:
					pretty_print = False

				if pretty_print:
					response = json.dumps(bot_config, indent=4)
				else:
					response = str(bot_config)

				self.send_buffer_size = len(response)

				return response

			case "set_value" | "set" | "s":
				try:
					key: str = args[1]
					value: str = args[2]
				except IndexError:
					return "No key or value provided."

				try:
					update = args[3] == "update" or args[3] == "u"
				except IndexError:
					update = False

				await self.config_manager.set_value(key, value, update)

				return f"Set {key} to {value}. The management portal has " + ("not " if not update else "") + "been updated."

			case "sync_from_portal" | "sync" | "sy":
				await self.config_manager.load_deferred_configs(self.bot.guilds)
				return "Reloaded configuration data from the management portal."
