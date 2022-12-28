from Framework.ManagementPortal.APIEndpoints import APIEndpoints
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


class QuotesAPI(ManagementPortalHandler):

    def __int__(self):
        return 0

    async def get_quote(self, guild_id: int, quote_id: int) -> dict:
        headers = self.base_headers.copy()
        headers["guild_id"] = str(guild_id)

        # If the quote ID is -1, then we want to get a random quote
        if quote_id == -1:
            headers["random"] = "true"
        else:
            headers["id"] = str(quote_id)

        return await self.get(APIEndpoints.GET_QUOTE, headers)

    async def add_quote(self, guild_id: int, content: str, author: int, quoted_by: int) -> dict:
        headers = self.base_headers.copy()
        headers["guild_id"] = str(guild_id)
        headers["content"] = content
        headers["author"] = str(author)
        headers["quoted_by"] = str(quoted_by)

        return await self.get(APIEndpoints.ADD_QUOTE, headers)

    async def remove_quote(self, guild_id: int, quote_id: int) -> dict:
        headers = self.base_headers.copy()
        headers["guild_id"] = str(guild_id)
        headers["quote_id"] = str(quote_id)

        return await self.get(APIEndpoints.REMOVE_QUOTE, headers)

    async def get_total_quotes(self, guild_id: int) -> dict:
        headers = self.base_headers.copy()
        headers["guild_id"] = str(guild_id)

        return await self.get(APIEndpoints.GET_QUOTE_COUNT, headers)

    async def edit_quote(self, guild_id: int, quote_id: int, content: str, author: int) -> dict:
        headers = self.base_headers.copy()
        headers["guild_id"] = str(guild_id)
        headers["quote_id"] = str(quote_id)
        headers["content"] = content
        headers["author"] = str(author)

        return await self.post(APIEndpoints.EDIT_QUOTE, headers)

    async def search_quotes(self, guild_id: int, search_type: str, author_id: int = -1, search_term: str = "", page: int = 0) -> dict:
        headers = self.base_headers.copy()
        headers["guild_id"] = str(guild_id)
        headers["search_type"] = search_type
        headers["page"] = page

        if search_type == "author":
            headers["author_id"] = str(author_id)
        elif search_type == "content":
            headers["search_term"] = search_term
        else:
            raise ValueError("Invalid search type")

        return await self.get(APIEndpoints.SEARCH_QUOTES, headers)

    async def list_recent_quotes(self, guild_id: int) -> dict:
        headers = self.base_headers.copy()
        headers["guild_id"] = str(guild_id)

        return await self.get(APIEndpoints.LIST_RECENT_QUOTES, headers)
