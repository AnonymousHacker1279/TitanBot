import os

import discord
import psutil

from Framework.ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class Status(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "status"

		with open(os.getcwd() + "/Resources/status.txt", 'r') as f:
			self.status_text = f.read()

	async def execute(self, args: list[str]) -> str:
		cpu_usage = psutil.cpu_percent(0.1) / 100
		cpu_color = self.get_color(cpu_usage)
		cpu_info = f"[color={cpu_color}]{cpu_usage * 100}%[/color]"

		mem_usage = psutil.virtual_memory()[2] / 100
		mem_color = self.get_color(mem_usage)
		mem_info = f"[color={mem_color}]{mem_usage * 100}%[/color]"

		disk_usage = psutil.disk_usage('/')[3] / 100
		disk_color = self.get_color(disk_usage)
		disk_info = f"[color={disk_color}]{disk_usage * 100}%[/color]"

		text = (self.status_text
				.replace("#a#", cpu_info)
				.replace("#b#", str(psutil.cpu_count()))
				.replace("#c#", mem_info)
				.replace("#d#", str(round(psutil.virtual_memory()[0] / (1024 * 1024 * 1024), 2)))
				.replace("#e#", disk_info)
				.replace("#f#", str(round(psutil.disk_usage('/')[0] / (1024 * 1024 * 1024), 2))))

		self.send_buffer_size = len(text)

		return text

	async def get_help_message(self) -> str:
		msg = "Get system status information."
		args = {}

		return await self.format_help_message(msg, args)
