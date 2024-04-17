import discord

from Framework.ConfigurationManager import ConfigurationManager
from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class GetLog(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "get_log"

	async def execute(self, args: list[str]) -> str:
		# Read the log file and send its contents back to the client
		with open(ThreadedLogger.log_file_path, 'r') as f:
			log_contents = f.read()

		self.send_buffer_size = len(log_contents)
		return log_contents.rstrip("\n")

	async def get_help_message(self) -> str:
		msg = "Print the log file to the console."
		args = {}

		return await self.format_help_message(msg, args)
