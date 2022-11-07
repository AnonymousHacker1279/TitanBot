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
from Framework.FileSystemAPI.ConfigurationManager import BotStatus, ConfigurationValues
from Framework.FileSystemAPI.ConfigurationManager.ConfigurationManager import ConfigurationManager
from Framework.FileSystemAPI.DataMigration import DataMigrator
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.FileSystemAPI.UpdateManager.UpdateManager import UpdateManager
from Framework.GeneralUtilities import CommandAccess, GeneralUtilities
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler

if __name__ == "__main__":

	database_version = 5
	ConfigurationValues.VERSION = "v2.4.0-indev"
	ConfigurationValues.COMMIT = GeneralUtilities.get_git_revision_short_hash()

	intents = discord.Intents.all()
	bot = bridge.Bot(command_prefix=commands.when_mentioned_or("$"), intents=intents)
	bot.help_command = Help()

	configuration_manager = ConfigurationManager()
	GeneralUtilities.run_and_get(configuration_manager.load_configs())

	management_portal_handler = ManagementPortalHandler(bot, configuration_manager)

	FileAPI.initialize(management_portal_handler)
	DataMigrator.initialize(management_portal_handler)

	logger = ThreadedLogger("TitanBot", management_portal_handler)
	logger.log_info("TitanBot " + ConfigurationValues.VERSION + " @ " + ConfigurationValues.COMMIT + " starting up")

	quotes_module = Quotes(management_portal_handler)

	bot.add_cog(quotes_module)
	bot.add_cog(Fun(management_portal_handler))
	bot.add_cog(Utility(management_portal_handler))
	bot.add_cog(Genius(management_portal_handler))
	bot.add_cog(RevokeAccess(management_portal_handler))
	bot.add_cog(CustomCommands(management_portal_handler))


	@bot.event
	async def on_ready():
		logger.log_info("TitanBot has connected to Discord")
		await bot.change_presence(activity=discord.Game(name="Initializing..."), status=discord.Status.dnd)

		# Check storage metadata, and perform migration as necessary
		logger.log_info("Checking guild storage metadata")
		await FileAPI.check_storage_metadata(database_version, bot.guilds)

		# Update local configurations and load deferred config values
		await management_portal_handler.command_handler.handle_command("update_configuration", True)
		await configuration_manager.load_deferred_configs(management_portal_handler, bot.guilds)

		# Do post-initialization for objects with a database cache
		logger.log_info("Performing post-initialization for objects with a database cache")
		await CommandAccess.post_initialize(bot, management_portal_handler)
		await Quotes.post_initialize(quotes_module, bot)

		# Initialize the update manager and check for updates if enabled
		update_manager = UpdateManager(management_portal_handler, configuration_manager, bot)
		if ConfigurationValues.AUTO_UPDATE_ENABLED:
			await update_manager.check_for_updates()

		# Send the ready status to the management portal
		await management_portal_handler.on_ready(update_manager)

		# Set the bot status
		status_config = await configuration_manager.get_value("discord_status")
		status = await BotStatus.get_status(status_config["activity_level"], status_config["activity_text"],
											status_config["activity_url"], status_config["status_level"])
		await bot.change_presence(activity=status[0], status=status[1])
		logger.log_info("TitanBot is ready to go!")


	@bot.event
	async def on_command_error(ctx: commands.Context, error: commands.CommandError):
		logger.log_error("Error running command: " + str(error))
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
	async def on_guild_join(ctx: commands.Context):
		logger.log_info("TitanBot has joined a new guild: " + ctx.guild.name)
		logger.log_info("Updating storage metadata for new guild")
		await FileAPI.check_storage_metadata(database_version, bot.guilds)

		# Invalidate existing caches
		logger.log_info("Invalidating existing caches...")
		await CommandAccess.invalidate_caches()
		await quotes_module.invalidate_caches()
		# Re-initialize objects with a database cache
		await CommandAccess.post_initialize(bot, management_portal_handler)
		await Quotes.post_initialize(quotes_module, bot)
		logger.log_info("All caches invalidated")


	bot.run(ConfigurationValues.TOKEN)
