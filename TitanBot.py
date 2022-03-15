import json
import re
from os.path import isfile

import discord
from discord.ext import commands

from Framework.CommandGroups.CustomCommands import CustomCommands
from Framework.CommandGroups.Fun import Fun
from Framework.CommandGroups.Genius import Genius
from Framework.CommandGroups.Help import Help
from Framework.CommandGroups.Quotes import Quotes
from Framework.CommandGroups.RevokeAccess import RevokeAccess
from Framework.CommandGroups.UserConfig import UserConfig
from Framework.CommandGroups.Utility import Utility
from Framework.GeneralUtilities import Constants, GeneralUtilities, OsmiumInterconnect
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
bot.add_cog(CustomCommands())


@bot.event
async def on_ready():
	print('Connected to Discord!')
	await bot.change_presence(activity=discord.Game('Inflicting pain on humans'))


@bot.event
async def on_command_error(ctx, error):
	is_running_custom_command = False
	embed = discord.Embed(color=discord.Color.dark_blue(), description='')
	if isinstance(error, commands.errors.CommandInvokeError):
		embed.title = "Command Invocation Error"
		embed.description = "An error occurred while trying to execute the command.\n\n"
	elif isinstance(error, commands.errors.UserInputError):
		embed.title = "Invalid Syntax"
		embed.description = "A command was used improperly. Please see ``$help`` for command usage.\n\n"
	elif isinstance(error, commands.errors.CommandNotFound):
		# If a command is not found, try checking for a custom command.
		# First, we need to get the command. Unfortunately the method isn't exactly clean...
		command = re.findall("(\"[\\w\\s]+\")", str(error))[0]
		command = str(command).lstrip('"').rstrip('"')
		path = await GeneralUtilities.get_custom_commands_directory() + "\\" + command + ".js"

		arguments = re.findall("(\"[\\w\\s]+\")", ctx.message.content)

		with open(await GeneralUtilities.get_custom_commands_alias_database(), "r") as f:
			aliases = json.load(f)

		if isfile(path):
			with open(path, "r") as f:
				embed = await OsmiumInterconnect.execute_with_osmium(f.read(), arguments, embed)
			is_running_custom_command = True
		else:
			try:
				path = await GeneralUtilities.get_custom_commands_directory() + "\\" + aliases["aliases"][command] + ".js"
				with open(path, "r") as f:
					embed = await OsmiumInterconnect.execute_with_osmium(f.read(), arguments, embed)
				is_running_custom_command = True

			except (ValueError, TypeError, KeyError):
				embed.title = "Command Not Found"
				embed.description = "A matching command could not be found. Please see ``$help`` for commands.\n\n"
	else:
		embed.title = "Unspecified Error"
		embed.description = "An error was thrown during the handling of the command, but I don't know how to handle it.\n\n"

	if is_running_custom_command is False:
		embed.description += "Error: ``" + str(error) + "``"

	await ctx.send(embed=embed)


bot.run(Constants.TOKEN)
