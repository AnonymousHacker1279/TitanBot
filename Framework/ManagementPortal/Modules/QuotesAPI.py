import discord

from Framework.ManagementPortal.APIEndpoints import APIEndpoints
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


class QuotesAPI:

    def __init__(self, management_portal_handler: ManagementPortalHandler):
        self.mph = management_portal_handler

    async def get_quote(self, guild_id: int, quote_id: int) -> dict:
        data = self.mph.base_data.copy()
        data["guild_id"] = str(guild_id)

        # If the quote ID is -1, then we want to get a random quote
        if quote_id == -1:
            data["random"] = "true"
        else:
            data["id"] = str(quote_id)

        return await self.mph.get(APIEndpoints.GET_QUOTE, data)

    async def add_quote(self, guild_id: int, content: str, author: int, quoted_by: int) -> dict:
        data = self.mph.base_data.copy()
        data["guild_id"] = str(guild_id)
        data["content"] = content
        data["author"] = str(author)
        data["quoted_by"] = str(quoted_by)

        return await self.mph.get(APIEndpoints.ADD_QUOTE, data)

    async def remove_quote(self, guild_id: int, quote_id: int) -> dict:
        data = self.mph.base_data.copy()
        data["guild_id"] = str(guild_id)
        data["quote_id"] = str(quote_id)

        return await self.mph.get(APIEndpoints.REMOVE_QUOTE, data)

    async def get_total_quotes(self, guild_id: int) -> dict:
        data = self.mph.base_data.copy()
        data["guild_id"] = str(guild_id)

        return await self.mph.get(APIEndpoints.GET_QUOTE_COUNT, data)

    async def edit_quote(self, guild_id: int, quote_id: int, content: str, author: discord.User) -> None:
        data = self.mph.base_data.copy()
        data["guild_id"] = str(guild_id)
        data["quote_id"] = str(quote_id)
        data["content"] = content

        if author is None:
            author = ""
        else:
            author = str(author.id)
        data["author"] = author

        return await self.mph.post(APIEndpoints.EDIT_QUOTE, data)

    async def search_quotes(self, guild_id: int, search_type: str, author_id: int = -1, search_term: str = "", page: int = 0) -> dict:
        data = self.mph.base_data.copy()
        data["guild_id"] = str(guild_id)
        data["search_type"] = search_type
        data["page"] = page

        if search_type == "author":
            data["author_id"] = str(author_id)
        elif search_type == "content":
            data["search_term"] = search_term
        else:
            raise ValueError("Invalid search type")

        return await self.mph.get(APIEndpoints.SEARCH_QUOTES, data)

    async def list_recent_quotes(self, guild_id: int) -> dict:
        data = self.mph.base_data.copy()
        data["guild_id"] = str(guild_id)

        return await self.mph.get(APIEndpoints.LIST_RECENT_QUOTES, data)
