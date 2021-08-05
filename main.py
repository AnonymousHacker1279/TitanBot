import os
import discord
from random import choice
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
from random import randint
import time
from CheckCommandUtils import CheckCommandPerms

import MiscellaneousCategory
import ModeratorCategory
import UtilityCategory

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$', intents=intents)

lastErrorTime = time.perf_counter() - 30
currentUserInfractions_CommandNotFound = 0
currentUserInfractions_ImproperSyntax = 0

@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord!')
	bot.loop.create_task(Manager())
	await bot.change_presence(activity=discord.Game('Inflicting pain on humans'))

@bot.event
async def on_command_error(ctx, error):
	global lastErrorTime
	global currentUserInfractions_CommandNotFound
	global currentUserInfractions_ImproperSyntax
	if await CheckCommandPerms(ctx) == False:
		if isinstance(error, commands.errors.CommandInvokeError):
			print("Logging CommandInvokeError: \n" + str(error))
			choices = ('Whoah there buddy, try talking a little less.', 'Die', 'Stop talking, your words are like sandpaper to my brain.', 'Perhaps you should take a look at this: https://www.gotoquiz.com/how_retarded_are_you_10')
			response = choice(choices)
			await ctx.send(response)
		elif isinstance(error, commands.errors.CommandNotFound):
			if time.perf_counter() - 30 <= lastErrorTime:
				currentUserInfractions_CommandNotFound = currentUserInfractions_CommandNotFound + 1
				if (currentUserInfractions_CommandNotFound == 3):
					response = "You think this is funny don't you."
				if (currentUserInfractions_CommandNotFound == 4):
					response = "Don't test me, human."
				if (currentUserInfractions_CommandNotFound >= 5):
					random = randint(5, 15)
					dm = await ctx.message.author.create_dm()
					response = "I told you not to test me, you worthless pile of flesh."
					while random >= 0:
						random = random - 1
						await dm.send(response)
			else:
				lastErrorTime = time.perf_counter()
				currentUserInfractions_CommandNotFound = 1
			if currentUserInfractions_CommandNotFound <= 2:
				response = "That command doesn't exist you gourd. Use $help to see commands."
			await ctx.send(response)
		elif isinstance(error, commands.errors.UserInputError):
			if time.perf_counter() - 30 <= lastErrorTime:
				currentUserInfractions_ImproperSyntax = currentUserInfractions_ImproperSyntax + 1
				if (currentUserInfractions_ImproperSyntax == 3):
					response = "You think this is funny don't you."
				if (currentUserInfractions_ImproperSyntax == 4):
					response = "Don't test me, human."
				if (currentUserInfractions_ImproperSyntax >= 5):
					random = randint(5, 15)
					dm = await ctx.message.author.create_dm()
					response = "I told you not to test me, you worthless pile of flesh."
					while random >= 0:
						random = random - 1
						await dm.send(response)
			else:
				lastErrorTime = time.perf_counter()
				currentUserInfractions_ImproperSyntax = 1
			if currentUserInfractions_ImproperSyntax <= 2:
				response = "Improper syntax you dweeb. Use $help to see command arguments."
			await ctx.send(response)
		else:
			print("Logging Error: \n" + str(error))
			response = "Something isn't right. Most likely this is my father's fault in programming me, otherwise screw you."
			await ctx.send(response)

class CustomHelpCommand(commands.MinimalHelpCommand):
	async def send_pages(self):
		destination = self.get_destination()
		e = discord.Embed(color=discord.Color.dark_blue(), description='')
		for page in self.paginator.pages:
			e.description += page
		await destination.send(embed=e)

async def Manager():
	global lastErrorTime
	global currentUserInfractions_CommandNotFound
	global currentUserInfractions_ImproperSyntax
	while True:
		if time.perf_counter() - 30 >= lastErrorTime and currentUserInfractions_CommandNotFound != 0:
			currentUserInfractions_CommandNotFound = 0
		if time.perf_counter() - 30 >= lastErrorTime and currentUserInfractions_ImproperSyntax != 0:
			currentUserInfractions_ImproperSyntax = 0
		await asyncio.sleep(10)

bot.help_command = CustomHelpCommand()
bot.add_cog(ModeratorCategory.Moderators())
bot.add_cog(UtilityCategory.Utility())
bot.add_cog(MiscellaneousCategory.Miscellaneous())
bot.run(TOKEN)