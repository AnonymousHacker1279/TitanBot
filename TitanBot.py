import discord
from discord.ext import commands

from Framework.CommandGroups.CustomCommands import CustomCommands
from Framework.CommandGroups.Fun import Fun
from Framework.CommandGroups.Genius import Genius
from Framework.CommandGroups.Quotes import Quotes
from Framework.CommandGroups.RevokeAccess import RevokeAccess
from Framework.CommandGroups.Utility import Utility
from Framework.FileSystemAPI import FileAPI
from Framework.GeneralUtilities import CommandAccess, Constants
from Framework.ModuleSystem.Modules import ModuleSystem

if __name__ == "__main__":

	intents = discord.Intents.all()
	bot = commands.Bot(intents=intents)

	quotes_module = Quotes()

	bot.add_cog(ModuleSystem())
	bot.add_cog(quotes_module)
	bot.add_cog(Fun())
	bot.add_cog(Utility())
	bot.add_cog(Genius())
	bot.add_cog(RevokeAccess())
	bot.add_cog(CustomCommands())


	@bot.event
	async def on_ready():
		print('Connected to Discord!')

		# Check storage metadata, and perform migration as necessary
		await FileAPI.check_storage_metadata(4, bot.guilds)

		# Do post-initialization for objects with a database cache
		await CommandAccess.post_initialize(bot)
		await Quotes.post_initialize(quotes_module, bot)

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
			embed.description = "A command was used improperly. Please read the descriptions for command usage.\n\n"
		else:
			embed.title = "Unspecified Error"
			embed.description = "An error was thrown during the handling of the command, but I don't know how to handle it.\n\n"

		if is_running_custom_command is False:
			embed.description += "Error: ``" + str(error) + "``"

		await ctx.send(embed=embed)


	bot.run(Constants.TOKEN)
