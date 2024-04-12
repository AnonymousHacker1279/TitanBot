import time

import aiohttp
import discord

from BasicCommand import BasicCommand
from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.GeneralUtilities import GeneralUtilities


class Ping(BasicCommand):

	def __init__(self, bot: discord.bot.Bot):
		super().__init__(bot)
		self.friendly_name = "ping"

	def execute(self, args: list[str]) -> str:
		# If no arguments are provided, default to both sources
		if not args:
			return f"{self.discord_portal_ping()}\n{GeneralUtilities.run_and_get(self.management_portal_ping())}"
		else:
			# Check the first argument to determine the source
			match args[0]:
				case "discord_portal" | "discord":
					return self.discord_portal_ping()
				case "management_portal" | "mp":
					return GeneralUtilities.run_and_get(self.management_portal_ping())
				case "all":
					return f"{self.discord_portal_ping()}\n{GeneralUtilities.run_and_get(self.management_portal_ping())}"
				case _:
					return "Invalid source. Must be either 'discord_portal' (discord) or 'management_portal' (mp)."

	def discord_portal_ping(self) -> str:
		discord_portal_latency: int = round(self.bot.latency * 1000)
		return f"Discord API Portal Ping: {self.color_text(f"{discord_portal_latency} ms", self.get_color(discord_portal_latency))}"

	async def management_portal_ping(self) -> str:
		start_time = time.time()

		# Send a GET request to the management portal URL
		async with aiohttp.ClientSession() as session:
			async with session.get(ConfigurationValues.MANAGEMENT_PORTAL_URL):
				end_time = time.time()
				latency = round((end_time - start_time) * 1000)

				return f"Management Portal Ping: {self.color_text(f"{latency} ms", self.get_color(latency))}"

	def get_color(self, latency: int):
		"""Calculate a color between green and red based on latency, normalized between 0 and 500."""
		percent = latency / 500
		return super().get_color(percent)
