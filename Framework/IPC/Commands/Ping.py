import time

import discord

from ConfigurationManager import ConfigurationManager
from Framework.ConfigurationManager import ConfigurationValues
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class Ping(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "ping"

	async def execute(self, args: list[str]) -> str:
		# If no arguments are provided, default to both sources
		if not args:
			return f"{self.discord_portal_ping()}\n{await self.management_portal_ping()}"
		else:
			# Check the first argument to determine the source
			match args[0]:
				case "discord_portal" | "discord":
					return self.discord_portal_ping()
				case "management_portal" | "mp":
					return await self.management_portal_ping()
				case "all":
					return f"{self.discord_portal_ping()}\n{await self.management_portal_ping()}"
				case _:
					return "Invalid source. Must be either 'discord_portal' (discord) or 'management_portal' (mp)."

	def discord_portal_ping(self) -> str:
		discord_portal_latency: int = round(self.bot.latency * 1000)
		return f"Discord API Portal Ping: {self.color_text(f"{discord_portal_latency} ms", self.get_color(discord_portal_latency))}"

	async def management_portal_ping(self) -> str:
		start_time = time.time()

		# Send a POST request to the management portal URL
		await self.config_manager.mph.post(ConfigurationValues.MANAGEMENT_PORTAL_URL)

		end_time = time.time()
		latency = round((end_time - start_time) * 1000)

		return f"Management Portal Ping: {self.color_text(f"{latency} ms", self.get_color(latency))}"

	def get_color(self, latency: int):
		"""Calculate a color between green and red based on latency, normalized between 0 and 500."""
		percent = latency / 500
		return super().get_color(percent)

	async def get_help_message(self) -> str:
		msg = "Get the latency between the bot and the Discord API Portal, and the bot and the Management Portal. If no source is provided, both sources will be checked."
		args = {
			"source": {
				"description": "The source to check the latency for.",
				"arguments": {
					"discord_portal": {
						"description": "Check the latency between the bot and the Discord API Portal.",
						"arguments": {}
					},
					"management_portal": {
						"description": "Check the latency between the bot and the Management Portal.",
						"arguments": {}
					},
					"all": {
						"description": "Check the latency between the bot and both portals. This is the default action.",
						"arguments": {}
					}
				}
			}
		}

		return await self.format_help_message(msg, args)
