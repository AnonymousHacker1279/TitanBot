import discord

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand


class Shutdown(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager):
		super().__init__(bot, config_manager)
		self.friendly_name = "shutdown"

	async def execute(self, args: list[str]) -> str:
		logger = await self.create_logger("IPCShutdown")

		logger.log_info("Shutdown command received from IPC server, shutting down...")
		self.extra_metadata["shutdown"] = True

		return ""
