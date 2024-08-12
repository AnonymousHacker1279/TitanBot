import os

import discord

from Framework.ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class Clean(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "clean"

	async def execute(self, args: list[any]) -> str:
		if not args:
			# Delete all temporary files
			temp_file_count = 0
			overall_size = 0
			for file in os.listdir(f"{os.getcwd()}/Storage/Temp"):
				temp_file_count += 1
				overall_size += os.path.getsize(f"{os.getcwd()}/Storage/Temp/{file}")
				os.remove(f"{os.getcwd()}/Storage/Temp/{file}")

			return f"{temp_file_count} temporary files have been deleted."

		if args[0] == "file_count":
			# Count the number of temporary files
			temp_file_count = 0
			overall_size = 0
			for file in os.listdir(f"{os.getcwd()}/Storage/Temp"):
				temp_file_count += 1
				overall_size += os.path.getsize(f"{os.getcwd()}/Storage/Temp/{file}")

			size_kb = round(overall_size / 1024, 2)
			size_mb = round(size_kb / 1024, 2)
			return f"There are {temp_file_count} temporary files, consuming {overall_size} bytes ({size_kb} KB, {size_mb} MB)."

	async def get_help_message(self) -> str:
		msg = "Manage and clean up temporary files."
		args = {
			"file_count": {
				"description": "Get the number of temporary files and the total size they consume.",
				"arguments": {}
			},
			"clean": {
				"description": "Delete all temporary files.",
				"arguments": {}
			}
		}

		return await self.format_help_message(msg, args)
