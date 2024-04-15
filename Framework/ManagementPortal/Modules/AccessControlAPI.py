from Framework.ManagementPortal.APIEndpoints import APIEndpoints
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


class AccessControlAPI:

	def __init__(self, management_portal_handler: ManagementPortalHandler):
		self.mph = management_portal_handler

	async def toggle_command_access(self, user_id: int, guild_id: int, module_name: str, command_name: str) -> dict:
		headers = self.mph.base_data.copy()
		headers["user_id"] = str(user_id)
		headers["guild_id"] = str(guild_id)
		headers["command_name"] = command_name + "[" + module_name + "]"

		return await self.post(APIEndpoints.TOGGLE_FEATURE_ACCESS, headers)

	async def toggle_module_access(self, user_id: int, guild_id: int, module_name: str) -> dict:
		headers = self.mph.base_data.copy()
		headers["user_id"] = str(user_id)
		headers["guild_id"] = str(guild_id)
		headers["module_name"] = module_name

		return await self.mph.post(APIEndpoints.TOGGLE_FEATURE_ACCESS, headers)

	async def get_banned_commands(self, user_id: int, guild_id: int) -> dict:
		headers = self.mph.base_data.copy()
		headers["user_id"] = str(user_id)
		headers["guild_id"] = str(guild_id)

		return await self.mph.get(APIEndpoints.GET_USER_BANNED_COMMANDS, headers)

	async def get_banned_modules(self, user_id: int, guild_id: int) -> dict:
		headers = self.mph.base_data.copy()
		headers["user_id"] = str(user_id)
		headers["guild_id"] = str(guild_id)

		return await self.mph.get(APIEndpoints.GET_USER_BANNED_MODULES, headers)
