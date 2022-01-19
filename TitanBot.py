import discord
from discord.ext import commands

from Framework.CommandGroups.Fun import Fun
from Framework.CommandGroups.Genius import Genius
from Framework.CommandGroups.Help import Help
from Framework.CommandGroups.Quotes import Quotes
from Framework.CommandGroups.RevokeAccess import RevokeAccess
from Framework.CommandGroups.UserConfig import UserConfig
from Framework.CommandGroups.Utility import Utility
from Framework.GeneralUtilities import Constants
from Framework.ModuleSystem.Modules import ModuleSystem

intents = discord.Intents.default()
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix='$', intents=intents)

bot.help_command = Help()

bot.add_cog(ModuleSystem())
bot.add_cog(UserConfig())
bot.add_cog(Quotes())
bot.add_cog(Fun())
bot.add_cog(Utility())
bot.add_cog(Genius())
bot.add_cog(RevokeAccess())


@bot.event
async def on_ready():
	print('Connected to Discord!')
	await bot.change_presence(activity=discord.Game('Inflicting pain on humans'))


@bot.event
async def on_command_error(ctx, error):
	embed = discord.Embed(color=discord.Color.dark_blue(), description='')
	if isinstance(error, commands.errors.CommandInvokeError):
		embed.title = "Command Invocation Error"
		embed.description = "An error occurred while trying to execute the command.\n\n"
	elif isinstance(error, commands.errors.UserInputError):
		embed.title = "Invalid Syntax"
		embed.description = "A command was used improperly. Please see ``$help`` for command usage.\n\n"
	elif isinstance(error, commands.errors.CommandNotFound):
		embed.title = "Command Not Found"
		embed.description = "A matching command could not be found. Please see ``$help`` for commands.\n\n"
	else:
		embed.title = "Unspecified Error"
		embed.description = "An error was thrown during the handling of the command, but I don't know how to handle it.\n\n"

	embed.description += "Error: ``" + str(error) + "``"

	await ctx.send(embed=embed)


bot.run(Constants.TOKEN)
