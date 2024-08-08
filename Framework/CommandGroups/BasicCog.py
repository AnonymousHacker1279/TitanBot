from discord.ext import commands

from Framework.SQLBridge import sql_bridge


class BasicCog(commands.Cog):

	def __init__(self):
		from Framework.ManagementPortal import management_portal_handler
		self.mph = management_portal_handler
		self.sql_bridge = sql_bridge

	async def update_usage_analytics(self, module_name: str, command_name: str, guild_id: int):
		await self.sql_bridge.update_command_used(guild_id, command_name, module_name)

	async def post_init(self) -> None:
		"""Runs during the bot on_ready event, after all configurations have loaded."""
		pass
