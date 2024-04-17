import discord

from Framework.ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class Shutdown(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "shutdown"

	async def execute(self, args: list[str]) -> str:
		logger = await self.create_logger("IPCShutdown")

		logger.log_info("Shutdown command received from IPC server, shutting down...")
		self.extra_metadata["shutdown"] = True

		return ""

	async def get_help_message(self) -> str:
		msg = "Shutdown the bot."
		args = {}

		return await self.format_help_message(msg, args)
