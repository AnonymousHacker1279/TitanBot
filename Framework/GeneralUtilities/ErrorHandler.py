import discord
from discord import errors
from discord.ext import commands

from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger


async def handle_error(ctx: discord.ApplicationContext, error: commands.CommandError, logger: ThreadedLogger) -> discord.Embed:
	"""
	Handles an error that occurred during the execution of a command.

	:param error: The error that occurred.
	:param logger: The logger to use for writing the error.
	"""

	embed = discord.Embed(color=discord.Color.dark_blue(), description='')

	should_log = True

	if isinstance(error, errors.ApplicationCommandInvokeError):
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

	embed.description += "```" + str(error) + "```"

	if should_log:
		embed.set_footer(text="This error has been logged.")
		logger.log_error(f"Error running command {ctx.command.name}: {error}")

	return embed
