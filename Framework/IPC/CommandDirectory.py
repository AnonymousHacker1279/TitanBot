import os
import time

from Framework.FileSystemAPI.ConfigurationManager import configuration_manager
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.IPC.BasicCommand import BasicCommand
from Framework.ManagementPortal import management_portal_handler


class CommandDirectory:

	def __init__(self, directory):
		self.logger = ThreadedLogger("CommandDirectory")
		self.directory = directory
		self.commands = {}

	def load_commands(self):
		start_time = time.time()

		for file in os.listdir(self.directory):
			if file.endswith(".py") and file != "__init__.py":
				command = file[:-3]
				module = __import__("Framework.IPC.Commands." + command, fromlist=[command])
				command_class = getattr(module, command)

				# Check if the command is a subclass of BasicCommand
				if issubclass(command_class, BasicCommand):
					command_instance = command_class(management_portal_handler.bot, configuration_manager)
					friendly_name = command_instance.friendly_name
					self.commands[friendly_name] = command_class

					self.logger.log_debug("Loaded console command: " + friendly_name)

		load_time: str = "{:.3f}".format(time.time() - start_time)
		self.logger.log_debug("Loaded " + str(len(self.commands)) + " commands in " + load_time + " seconds")

	def get_command(self, command):
		if command in self.commands:
			return self.commands[command]
		else:
			return None
