from discord.ext import commands

from Framework.ManagementPortal.APIEndpoints import APIEndpoints


class BasicCog(commands.Cog):

	def __init__(self):
		from Framework.ManagementPortal import management_portal_handler
		self.mph = management_portal_handler

	async def update_management_portal_command_used(self, module_name: str, command_name: str, guild_id: int):
		data = self.mph.base_data.copy()
		data["module_name"] = module_name
		data["command_name"] = command_name
		data["guild_id"] = str(guild_id)

		await self.mph.post(APIEndpoints.UPDATE_COMMAND_USED, data)

	async def post_init(self) -> None:
		"""Runs during the bot on_ready event, after all configurations have loaded."""
		pass
