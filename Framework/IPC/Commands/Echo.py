import discord

from Framework.ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class Echo(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "echo"

	async def execute(self, args: list[str]) -> str:
		if not args:
			return "No arguments provided."

		if args[0].startswith("color="):
			self.color = args[0].split("=")[1]
			args = args[1:]

		return "Echo: " + " ".join(args)

	async def get_help_message(self) -> str:
		msg = "Echo a message back to the user. May be useful for testing some IPC features."
		args = {
			"message": {
				"description": "The message to echo back to the user. If it starts with 'color=', the color of the message will be set to the provided value.",
				"arguments": {}
			}
		}

		return await self.format_help_message(msg, args)
