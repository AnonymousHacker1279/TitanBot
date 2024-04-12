import discord

from BasicCommand import BasicCommand
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger


class GetLog(BasicCommand):

	def __init__(self, bot: discord.bot.Bot):
		super().__init__(bot)
		self.friendly_name = "get_log"

	def execute(self, args: list[str]) -> str:
		# Read the log file and send its contents back to the client
		with open(ThreadedLogger.log_file_path, 'r') as f:
			log_contents = f.read()

		self.send_buffer_size = len(log_contents)
		return log_contents.rstrip("\n")
