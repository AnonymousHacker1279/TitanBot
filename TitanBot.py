import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import Framework.ModuleSystem.Modules as ModuleSystem
import Framework.Commands.Quotes as Quotes
import Framework.Commands.HelpCommand as HelpCommand

class TitanBot(discord.Client):

	load_dotenv()
	TOKEN = os.getenv('DISCORD_TOKEN')
	GUILD = os.getenv('DISCORD_GUILD')

	intents = discord.Intents.default()
	intents.members = True
	global bot
	bot = commands.Bot(command_prefix='$', intents=intents)

	@bot.event
	async def on_ready():
		print(f'{bot.user} has connected to Discord!')
		await bot.change_presence(activity=discord.Game('Inflicting pain on humans'))

	bot.help_command = HelpCommand.Help()

	bot.add_cog(ModuleSystem.ModuleSystem())
	bot.add_cog(Quotes.Quotes())

	bot.run(TOKEN)