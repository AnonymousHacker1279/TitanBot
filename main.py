import os
import discord
from random import choice
from dotenv import load_dotenv
from discord.ext import commands

import MiscellaneousCategory
import ModeratorCategory
import UtilityCategory

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	await bot.change_presence(activity=discord.Game('Inflicting pain on humans'))

@bot.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.errors.CommandInvokeError):
		print("Logging CommandInvokeError: \n" + str(error))
		choices = ('Whoah there buddy, try talking a little less.', 'Die', 'Stop talking, your words are like sandpaper to my brain.', "Perhaps you should take a look at this: https://www.gotoquiz.com/how_retarded_are_you_10")
		response = choice(choices)
		await ctx.send(response)

class CustomHelpCommand(commands.MinimalHelpCommand):
	async def send_pages(self):
		destination = self.get_destination()
		e = discord.Embed(color=discord.Color.dark_blue(), description='')
		for page in self.paginator.pages:
			e.description += page
		await destination.send(embed=e)

bot.help_command = CustomHelpCommand()
bot.add_cog(ModeratorCategory.Moderators())
bot.add_cog(UtilityCategory.Utility())
bot.add_cog(MiscellaneousCategory.Miscellaneous())
bot.run(TOKEN)