from Framework.ManagementPortal.APIEndpoints import APIEndpoints
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


class DataMigrationAPI(ManagementPortalHandler):

    def __int__(self):
        return 0

    async def migrate_quotes(self, guild_id: int, quotes_json: str):
        headers = self.base_headers.copy()
        headers["guild_id"] = str(guild_id)
        headers["quotes"] = quotes_json

        await self.post(APIEndpoints.MIGRATE_QUOTES, headers)
