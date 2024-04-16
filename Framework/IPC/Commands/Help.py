import discord

from ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class Help(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "help"

	async def execute(self, args: list[str]) -> str:
		if not args:
			return "Please specify a command to get help information for."

		command = self.command_directory.get_command(args[0])

		if command is None:
			return f"The provided command '{args[0]}' does not exist."

		return await command.get_help_message()

	async def get_help_message(self) -> str:
		msg = "Get help information for a command."
		args = {
			"command": {
				"description": "The command to get help information for.",
				"arguments": {}
			}
		}

		return await self.format_help_message(msg, args)
