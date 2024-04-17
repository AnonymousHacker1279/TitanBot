import os
import sys

import discord

from Framework.ConfigurationManager import ConfigurationManager, ConfigurationValues
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class About(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "about"
		self.color = "#0047AB"

		with open(os.getcwd() + "/Resources/about.txt", 'r') as f:
			self.about_text = f.read()

		self.about_text = (self.about_text
							.replace("#a#", ConfigurationValues.VERSION)
							.replace("#b#", str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]))
							.replace("#c#", str(discord.__version__)))

		self.send_buffer_size = len(self.about_text)

	async def execute(self, args: list[str]) -> str:
		return self.about_text

	async def get_help_message(self) -> str:
		msg = "Get information about the bot."
		args = {}

		return await self.format_help_message(msg, args)
