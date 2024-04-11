import os
import sys

from APIEndpoints import APIEndpoints
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger


class PortalCommandHandler:

	def __init__(self):
		from Framework.ManagementPortal import management_portal_handler

		self.logger = ThreadedLogger("PortalCommandHandler")
		self.mph = management_portal_handler

	async def parse_pending_commands(self, content):
		# Parse the command from the JSON data
		commands = []
		for command in content:
			if content[command] == 1:
				commands.append(command)

		# Handle the commands
		for command in commands:
			await self.handle_command(command)

	async def handle_command(self, command):
		# Portal commands are strings which refer to a bot action
		# They are sent to the bot via the management portal
		# This function handles the command and performs the appropriate action

		if command == "shutdown":
			# Shutdown the bot
			self.logger.log_info("Shutdown command received from management portal, shutting down")
			await self.__update_management_portal_command_completed(command)

			exit(0)
		elif command == "restart":
			# Restart the bot
			self.logger.log_info("Restart command received from management portal, restarting")
			await self.__update_management_portal_command_completed(command)

			python = sys.executable
			os.execl(python, python, *sys.argv)
		elif command == "update_configuration":
			# Update the bot configuration
			self.logger.log_info("Update configuration command received from management portal, updating configuration")
			await self.__update_management_portal_command_completed(command)

			await self.mph.cm.load_deferred_configs(self.mph, self.mph.bot.guilds)

	async def __update_management_portal_command_completed(self, command: str):
		headers = self.mph.base_headers.copy()
		headers["command"] = command

		await self.mph.post(APIEndpoints.UPDATE_COMMAND_COMPLETED, headers)
