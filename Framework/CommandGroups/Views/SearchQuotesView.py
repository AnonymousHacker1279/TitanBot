import math
from enum import Enum

import discord.ui

from Framework.GeneralUtilities import QuoteUtils
from Framework.SQLBridge import SQLBridge


class SearchTypes(str, Enum):
	AUTHOR = "author"
	CONTENT = "content"


class SearchQuotesView(discord.ui.View):

	def __init__(self, ctx: discord.ApplicationContext, bridge: SQLBridge,
				page: int, total_quotes: int, search_type: SearchTypes, author_id: int = None, content: str = None,
				descending_order: bool = False):
		super().__init__(timeout=180)
		self.ctx = ctx
		self.bridge = bridge
		self.page = page
		self.author_id = author_id
		self.content = content
		self.total_quotes = total_quotes
		self.search_type = search_type
		self.descending_order = descending_order

	@discord.ui.button(label="Previous Page", style=discord.ButtonStyle.blurple, emoji="⏪")
	async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.page -= 1
		embed, total_quotes = await self.search()

		await interaction.response.edit_message(embed=embed, view=await self.get_view())

	@discord.ui.button(label="Next Page", style=discord.ButtonStyle.blurple, emoji="⏩")
	async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
		self.page += 1
		embed, total_quotes = await self.search()

		await interaction.response.edit_message(embed=embed, view=await self.get_view())

	async def search(self):
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		if self.search_type == SearchTypes.AUTHOR:
			return await QuoteUtils.handle_searching_author(self.ctx, self.bridge, self.page, embed, self.author_id, self.descending_order)
		elif self.search_type == SearchTypes.CONTENT:
			return await QuoteUtils.handle_searching_content(self.ctx, self.bridge, self.page, embed, self.content, self.descending_order)

	async def get_view(self):
		view = SearchQuotesView(self.ctx, self.bridge, self.page, self.total_quotes, self.search_type, self.author_id, self.content, self.descending_order)

		if self.page <= 0:
			view.previous_page.disabled = True
		if self.page >= math.ceil(self.total_quotes / 10) - 1:
			view.next_page.disabled = True

		return view
