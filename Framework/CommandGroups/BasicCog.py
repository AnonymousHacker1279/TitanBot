import discord
from discord.ext import commands

from Framework.ConfigurationManager import ConfigurationManager
from Framework.GeneralUtilities import web_request_handler
from Framework.SQLBridge import sql_bridge


class BasicCog(commands.Cog):

	def __init__(self, bot: discord.Bot, configuration_manager: ConfigurationManager):
		self.sql_bridge = sql_bridge
		self.wbh = web_request_handler
		self.bot = bot
		self.cm: ConfigurationManager = configuration_manager

	async def update_usage_analytics(self, module_name: str, command_name: str, guild_id: int):
		await self.sql_bridge.update_command_used(guild_id, command_name, module_name)

	async def post_init(self) -> None:
		"""Runs during the bot on_ready event, after all configurations have loaded."""
		pass
