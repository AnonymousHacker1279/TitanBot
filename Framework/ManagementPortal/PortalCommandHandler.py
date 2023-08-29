import json
import os
import sys

from Framework.FileSystemAPI import DatabaseObjects
from Framework.FileSystemAPI.ConfigurationManager import BotStatus
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

	async def handle_command(self, command, impersonate: bool = False):
		# Portal commands are strings which refer to a bot action
		# They are sent to the bot via the management portal
		# This function handles the command and performs the appropriate action

		if command == "shutdown":
			# Shutdown the bot
			if not impersonate:
				self.logger.log_info("Shutdown command received from management portal, shutting down")
				await self.mph.update_management_portal_command_completed(command)

			exit(0)
		elif command == "restart":
			# Restart the bot
			if not impersonate:
				self.logger.log_info("Restart command received from management portal, restarting")
				await self.mph.update_management_portal_command_completed(command)

			python = sys.executable
			os.execl(python, python, *sys.argv)
		elif command == "update_configuration":
			# Update the bot configuration
			if not impersonate:
				self.logger.log_info("Update configuration command received from management portal, updating configuration")
				await self.mph.update_management_portal_command_completed(command)

			global_configuration = await self.mph.get_management_portal_configuration("global")

			# Write the new configuration to disk
			with open(await DatabaseObjects.get_global_configuration_database(), "w") as f:
				json.dump(global_configuration, f, indent=4)

			config_error_occurred = False
			for guild in self.mph.bot.guilds:
				with open(await DatabaseObjects.get_configuration_database(guild.id), "w") as f:
					server_specific_config = await self.mph.get_management_portal_configuration(guild.id)

					# Merge the global configuration with the server specific configuration values
					# If there is no server specific configuration, use the global configuration
					if server_specific_config is None:
						server_specific_config = {}
					config = global_configuration
					for group in server_specific_config:
						for key in server_specific_config[group]:
							try:
								config[group][key] = server_specific_config[group][key]
							except KeyError:
								self.logger.log_error("KeyError when merging global configuration with server specific configuration,"
													" a key may exist on the server specific configuration but not in the global configuration")
								self.logger.log_error("Offending entry, Key: " + key + ", Group: " + group)
								config_error_occurred = True
								pass

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

			if config_error_occurred:
				self.logger.log_error("An error occurred when updating the configuration, please check the logs for more information")
				self.logger.log_error("The bot will attempt to run but unexpected failures may occur")

			# Reload the configuration
			await self.mph.cm.load_deferred_configs(self.mph, self.mph.bot.guilds)
			self.logger.log_debug("Reloading deferred configurations")
			# Update the bot status
			status_config = await self.mph.cm.get_value("discord_status")
			status = await BotStatus.get_status(status_config["activity_level"], status_config["activity_text"],
												status_config["activity_url"], status_config["activity_emoji"],
												status_config["status_level"])
			await self.mph.bot.change_presence(activity=status[0], status=status[1])
