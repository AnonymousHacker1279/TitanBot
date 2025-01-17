import discord

from Framework.CommandGroups import custom_commands_loader
from Framework.ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class CustomCommandsManager(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "custom_commands_manager"

	async def execute(self, args: list[str]) -> str:
		if not args:
			return "No arguments provided."

		if args[0] == "reload":
			custom_commands_loader.unload_custom_cogs(self.bot)
			custom_commands_loader.load_custom_cogs(self.bot, self.config_manager)
		else:
			return "Invalid argument."

		return "Custom commands reloaded."

	async def get_help_message(self) -> str:
		msg = "Manage custom bot commands."
		args = {
			"reload": {
				"description": "Unload then reload all custom commands.",
				"arguments": {}
			}
		}

		return await self.format_help_message(msg, args)
