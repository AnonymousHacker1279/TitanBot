import discord
from discord.ext import commands


class Help(commands.MinimalHelpCommand):
	async def send_pages(self):
		destination = self.get_destination()
		e = discord.Embed(color=discord.Color.dark_blue(), description='')
		for page in self.paginator.pages:
			e.description += page
		await destination.send(embed=e)
