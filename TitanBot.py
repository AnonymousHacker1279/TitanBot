import discord
from discord.ext import bridge, commands

from Framework.CommandGroups.CustomCommands import CustomCommands
from Framework.CommandGroups.Fun import Fun
from Framework.CommandGroups.Genius import Genius
from Framework.CommandGroups.Help import Help
from Framework.CommandGroups.Quotes import Quotes
from Framework.CommandGroups.RevokeAccess import RevokeAccess
from Framework.CommandGroups.Utility import Utility
from Framework.FileSystemAPI import FileAPI
from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.FileSystemAPI.ConfigurationManager.ConfigurationManager import ConfigurationManager
from Framework.FileSystemAPI.DataMigration import DataMigrator
from Framework.FileSystemAPI.Logger import Logger
from Framework.GeneralUtilities import CommandAccess, GeneralUtilities
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler

if __name__ == "__main__":

	database_version = 5

	intents = discord.Intents.all()
	bot = bridge.Bot(command_prefix="$", intents=intents)
	bot.help_command = Help()

	configuration_manager = ConfigurationManager()
	GeneralUtilities.run_and_get(configuration_manager.load_configs())

	management_portal_handler = ManagementPortalHandler(bot, configuration_manager)

	FileAPI.initialize(management_portal_handler)
	DataMigrator.initialize(management_portal_handler)

	logger = Logger("TitanBot", management_portal_handler)

	quotes_module = Quotes(management_portal_handler)

	bot.add_cog(quotes_module)
	bot.add_cog(Fun(management_portal_handler))
	bot.add_cog(Utility(management_portal_handler))
	bot.add_cog(Genius(management_portal_handler))
	bot.add_cog(RevokeAccess(management_portal_handler))
	bot.add_cog(CustomCommands(management_portal_handler))


	@bot.event
	async def on_ready():
		await logger.log_info("TitanBot has connected to Discord")

		# Check storage metadata, and perform migration as necessary
		await logger.log_info("Checking guild storage metadata")
		await FileAPI.check_storage_metadata(database_version, bot.guilds)

		await configuration_manager.load_deferred_configs(management_portal_handler, bot.guilds)

		# Do post-initialization for objects with a database cache
		await logger.log_info("Performing post-initialization for objects with a database cache")
		await CommandAccess.post_initialize(bot, management_portal_handler)
		await Quotes.post_initialize(quotes_module, bot)

		await management_portal_handler.on_ready()

		await bot.change_presence(activity=discord.Game('Inflicting pain on humans'))
		await logger.log_info("TitanBot is ready to go!")


	@bot.event
	async def on_command_error(ctx, error):
		await logger.log_error("Error running command: " + str(error))
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

		await ctx.send(embed=embed)

	@bot.event
	async def on_guild_join(ctx):
		await logger.log_info("TitanBot has joined a new guild: " + ctx.name)
		await logger.log_info("Updating storage metadata for new guild")
		await FileAPI.check_storage_metadata(database_version, bot.guilds)

		# Invalidate existing caches
		await logger.log_info("Invalidating existing caches...")
		await CommandAccess.invalidate_caches()
		await quotes_module.invalidate_caches()
		# Re-initialize objects with a database cache
		await CommandAccess.post_initialize(bot, management_portal_handler)
		await Quotes.post_initialize(quotes_module, bot)
		await logger.log_info("All caches invalidated")


	bot.run(ConfigurationValues.TOKEN)
