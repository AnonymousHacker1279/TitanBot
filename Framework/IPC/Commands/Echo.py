import discord

from ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand


class Echo(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager):
		super().__init__(bot, config_manager)
		self.friendly_name = "echo"

	async def execute(self, args: list[str]) -> str:
		if not args:
			return "No arguments provided."

		if args[0].startswith("color="):
			self.color = args[0].split("=")[1]
			args = args[1:]

		return "Echo: " + " ".join(args)
