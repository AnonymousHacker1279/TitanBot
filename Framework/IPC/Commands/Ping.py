import discord

from Framework.ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class Ping(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "ping"

	async def execute(self, args: list[str]) -> str:
		return f"{self.discord_portal_ping()}"

	def discord_portal_ping(self) -> str:
		discord_portal_latency: int = round(self.bot.latency * 1000)
		return f"Discord API Portal Ping: {self.color_text(f"{discord_portal_latency} ms", self.get_color(discord_portal_latency))}"

	def get_color(self, latency: int):
		"""Calculate a color between green and red based on latency, normalized between 0 and 500."""
		percent = latency / 500
		return super().get_color(percent)

	async def get_help_message(self) -> str:
		msg = "Get the latency between the bot and the Discord API Portal."
		args = {}

		return await self.format_help_message(msg, args)
