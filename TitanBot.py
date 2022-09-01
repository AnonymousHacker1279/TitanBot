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
from Framework.GeneralUtilities import Constants, GeneralUtilities, OsmiumInterconnect, PermissionHandler
from Framework.ModuleSystem.Modules import ModuleSystem

if __name__ == "__main__":

	intents = discord.Intents.all()
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
			message_content = str(ctx.message.content)
			command = re.findall(re.compile(r"(\"[!@#$%^&~.,\w\s\]]+\")"), str(error))[0]
			command = str(command).lstrip('"').rstrip('"')
			message_content = message_content.replace("$" + command + " ", "")

			path = await GeneralUtilities.get_custom_commands_directory() + "\\" + command + ".js"

			arguments = await GeneralUtilities.arg_splitter(message_content)

			with open(await GeneralUtilities.get_custom_commands_metadata_database(), "r") as f:
				metadata = json.load(f)
				wizard_only = False
				if command in metadata["wizard_only_commands"]:
					wizard_only = True

			if isfile(path):
				embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																						command,
																						shouldCheckForWizard=wizard_only)
				if not failedPermissionCheck:
					with open(path, "r") as f:
						embed = await OsmiumInterconnect.execute_with_osmium(f.read(), arguments, embed)
				is_running_custom_command = True
			else:
				try:
					path = await GeneralUtilities.get_custom_commands_directory() + "\\" + metadata["aliases"][command] + ".js"
					embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																							command,
																							shouldCheckForWizard=wizard_only)
					if not failedPermissionCheck:
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
