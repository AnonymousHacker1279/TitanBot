import os
import sys

from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger


class PortalCommandHandler:

	def __init__(self, management_portal_handler):
		self.logger = ThreadedLogger("PortalCommandHandler", management_portal_handler)
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
			await self.mph.update_management_portal_command_completed(command)

			exit(0)
		elif command == "restart":
			# Restart the bot
			self.logger.log_info("Restart command received from management portal, restarting")
			await self.mph.update_management_portal_command_completed(command)

			python = sys.executable
			os.execl(python, python, *sys.argv)
		elif command == "update_configuration":
			# Update the bot configuration
			self.logger.log_info("Update configuration command received from management portal, updating configuration")
			await self.mph.update_management_portal_command_completed(command)

			await self.mph.cm.load_deferred_configs(self.mph, self.mph.bot.guilds)
