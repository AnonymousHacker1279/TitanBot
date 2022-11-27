import discord
from discord.ext import commands

from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger


async def handle_error(error: commands.CommandError, logger: ThreadedLogger):
	embed = discord.Embed(color=discord.Color.dark_blue(), description='')

	should_log = True

	if isinstance(error, commands.errors.CommandInvokeError):
		embed.title = "Command Invocation Error"
		embed.description = "An error occurred while trying to execute the command.\n\n"
	elif isinstance(error, commands.errors.UserInputError):
		embed.title = "Invalid Syntax"
		embed.description = "A command was used improperly. Please read the descriptions for command usage.\n\n"
	elif isinstance(error, commands.errors.CommandNotFound):
		embed.title = "Command Not Found"
		embed.description = "The command you entered does not exist.\n\n"

		should_log = False
	elif isinstance(error, commands.errors.NoPrivateMessage):
		embed.title = "Private Message Error"
		embed.description = "This command cannot be used in direct messages.\n\n"

		should_log = False
	else:
		embed.title = "Unspecified Error"
		embed.description = "An error was thrown during the handling of the command, but I don't know how to handle it.\n\n"

	if should_log:
		logger.log_error("Error running command: " + str(error))

	return embed
