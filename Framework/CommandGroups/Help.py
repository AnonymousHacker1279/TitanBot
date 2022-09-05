import discord
from discord.ext import commands


class Help(commands.MinimalHelpCommand):
	async def send_pages(self):
		destination = self.get_destination()
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		for page in self.paginator.pages:
			embed.description += page

		embed.set_footer(text="See the wiki at https://github.com/AnonymousHacker1279/TitanBot/wiki")

		await destination.send(embed=embed)