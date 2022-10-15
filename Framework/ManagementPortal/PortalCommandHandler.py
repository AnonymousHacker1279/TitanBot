import json
import os
import sys

from Framework.FileSystemAPI import DatabaseObjects
from Framework.FileSystemAPI.ConfigurationManager import BotStatus


class PortalCommandHandler:

	def __init__(self, logger, management_portal_handler):
		self.logger = logger
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
			await self.logger.log_info("Shutdown command received from management portal, shutting down")
			await self.mph.update_management_portal_command_completed(command)
			exit(0)
		elif command == "restart":
			# Restart the bot
			await self.logger.log_info("Restart command received from management portal, restarting")
			await self.mph.update_management_portal_command_completed(command)
			python = sys.executable
			os.execl(python, python, *sys.argv)
		elif command == "update_configuration":
			# Update the bot configuration
			await self.logger.log_info("Update configuration command received from management portal, updating configuration")
			await self.mph.update_management_portal_command_completed(command)

			global_configuration = await self.mph.get_management_portal_configuration("global")

			# Write the new configuration to disk
			with open(await DatabaseObjects.get_global_configuration_database(), "w") as f:
				json.dump(global_configuration, f, indent=4)

			for guild in self.mph.bot.guilds:
				with open(await DatabaseObjects.get_configuration_database(guild.id), "w") as f:
					server_specific_config = await self.mph.get_management_portal_configuration(guild.id)

					# Merge the global configuration with the server specific configuration values
					config = global_configuration
					for group in server_specific_config:
						for key in server_specific_config[group]:
							config[group][key] = server_specific_config[group][key]

					# Convert keys from strings if they are numbers or a boolean
					for group in config:
						for key in config[group]:
							try:
								if config[group][key].isdigit():
									config[group][key] = int(config[group][key])
								elif config[group][key].lower() == "true":
									config[group][key] = True
								elif config[group][key].lower() == "false":
									config[group][key] = False
							except AttributeError:
								pass

					json.dump(config, f, indent=4)

			# Reload the configuration
			await self.mph.cm.load_deferred_configs(self.mph, self.mph.bot.guilds)
			# Update the bot status
			status_config = await self.mph.cm.get_value("discord_status")
			status = await BotStatus.get_status(status_config["activity_level"], status_config["activity_text"],
												status_config["activity_url"], status_config["status_level"])
			await self.mph.bot.change_presence(activity=status[0], status=status[1])
