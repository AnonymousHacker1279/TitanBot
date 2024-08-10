from abc import abstractmethod

import discord

from Framework.ConfigurationManager import ConfigurationManager
from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger
from Framework.IPC.CommandDirectory import CommandDirectory


class BasicCommand:

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		self.bot = bot
		self.config_manager = config_manager
		self.command_directory = command_directory
		self.friendly_name = self.__class__.__name__.lower()
		self.send_buffer_size: int = 1024
		self.extra_metadata: dict[str, any] = {}
		self.color: str = "white"

	async def execute(self, args: list[any]) -> str:
		pass

	@abstractmethod
	async def get_help_message(self) -> str:
		pass

	async def format_help_message(self, message: str, arguments: dict[str, any], indent: str = "", is_top_level: bool = True) -> str:
		"""Format a help message."""
		help_message = f"{message}"

		if arguments:
			if is_top_level:
				help_message += "\n\nArguments:\n"
			is_top_level = False

			for command, command_info in arguments.items():
				if isinstance(command_info, dict):
					help_message += f"{indent} - [color=#FFDF00]{command}[/color]: {command_info['description']}\n"

					if command_info['arguments']:
						help_message += await self.format_help_message("", command_info['arguments'], indent + "   ", is_top_level)
				else:
					help_message += f"{indent} - [color=#FFDF00]{command}[/color]: {command_info}\n"

		return help_message

	def color_text(self, text: str, color: str):
		return f"[color={color}]{text}[/color]"

	def get_color(self, percent: float):
		"""Calculate a color between green and red based on a percentage."""
		if percent < 0:
			percent = 0
		if percent > 1:
			percent = 1

		# Calculate the color
		red = int(255 * percent)
		green = int(255 * (1 - percent))
		blue = 0

		# Convert to hex and return
		return '#{:02x}{:02x}{:02x}'.format(red, green, blue)

	async def create_logger(self, name: str) -> ThreadedLogger:
		return ThreadedLogger(name)
