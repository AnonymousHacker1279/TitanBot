import os
import sys

import discord

from BasicCommand import BasicCommand
from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues


class About(BasicCommand):

	def __init__(self, bot: discord.bot.Bot):
		super().__init__(bot)
		self.friendly_name = "about"
		self.color = "#0047AB"

		with open(os.getcwd() + "/Resources/about.txt", 'r') as f:
			self.about_text = f.read()

		self.about_text = (self.about_text
							.replace("#a#", ConfigurationValues.VERSION)
							.replace("#b#", str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]))
							.replace("#c#", str(discord.__version__)))

		self.send_buffer_size = len(self.about_text)

	def execute(self, args: list[str]) -> str:
		return self.about_text
