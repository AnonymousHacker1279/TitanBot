import os
import time

import discord

from Framework.ConfigurationManager import configuration_manager
from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger


class CommandDirectory:

	def __init__(self, directory):
		self.logger = ThreadedLogger("CommandDirectory")
		self.directory = directory
		self.commands = {}

	def load_commands(self, bot: discord.Bot) -> None:
		"""Load all commands from the directory specified in the constructor."""
		from Framework.IPC.BasicCommand import BasicCommand

		start_time = time.time()

		for file in os.listdir(self.directory):
			if file.endswith(".py") and file != "__init__.py":
				command = file[:-3]
				module = __import__("Framework.IPC.Commands." + command, fromlist=[command])
				command_class = getattr(module, command)

				# Check if the command is a subclass of BasicCommand
				if issubclass(command_class, BasicCommand):
					command_instance = command_class(bot, configuration_manager, self)
					friendly_name = command_instance.friendly_name
					self.commands[friendly_name] = command_instance

					self.logger.log_debug("Loaded console command: " + friendly_name)

		load_time: str = "{:.3f}".format(time.time() - start_time)
		self.logger.log_debug("Loaded " + str(len(self.commands)) + " commands in " + load_time + " seconds")

	def get_command(self, command):
		"""
		Get a command by its friendly name.

		:param command: The friendly name of the command to get.
		:return: The command object or None if the command does not exist.
		"""

		if command in self.commands:
			return self.commands[command]
		else:
			return None
