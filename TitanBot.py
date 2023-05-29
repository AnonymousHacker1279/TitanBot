import atexit

import discord
from discord.ext import commands

from Framework.CommandGroups.AccessControl import AccessControl
from Framework.CommandGroups.CurseForge import CurseForge
from Framework.CommandGroups.CustomCommands import CustomCommands
from Framework.CommandGroups.Fun import Fun
from Framework.CommandGroups.Genius import Genius
from Framework.CommandGroups.Help import Help
from Framework.CommandGroups.Quotes import Quotes
from Framework.CommandGroups.Utility import Utility
from Framework.FileSystemAPI import FileAPI
from Framework.FileSystemAPI.ConfigurationManager import BotStatus, ConfigurationValues
from Framework.FileSystemAPI.ConfigurationManager.ConfigurationManager import ConfigurationManager
from Framework.FileSystemAPI.DataMigration.DataMigrator import DataMigrator
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.FileSystemAPI.UpdateManager.UpdateManager import UpdateManager
from Framework.GeneralUtilities import ErrorHandler, ExitHandler, GeneralUtilities
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler
from Framework.Osmium.Osmium import Osmium

if __name__ == "__main__":

	database_version = 7
	ConfigurationValues.VERSION = "v2.7.0-indev"
	ConfigurationValues.COMMIT = GeneralUtilities.get_git_revision_short_hash()

	intents = discord.Intents.all()
	bot = discord.Bot(intents=intents)
	bot.help_command = Help()

	configuration_manager = ConfigurationManager()
	GeneralUtilities.run_and_get(configuration_manager.load_configs())

	management_portal_handler = ManagementPortalHandler(bot, configuration_manager)

	FileAPI.initialize(management_portal_handler)
	data_migrator = DataMigrator(management_portal_handler)

	logger = ThreadedLogger("TitanBot", management_portal_handler)
	logger.log_info("TitanBot " + ConfigurationValues.VERSION + " @ " + ConfigurationValues.COMMIT + " starting up")

	osmium = Osmium(management_portal_handler)

	custom_commands_module = CustomCommands(management_portal_handler, osmium)

	bot.add_cog(Quotes(management_portal_handler))
	bot.add_cog(Fun(management_portal_handler))
	bot.add_cog(Utility(management_portal_handler))
	bot.add_cog(Genius(management_portal_handler))
	bot.add_cog(AccessControl(management_portal_handler))
	bot.add_cog(custom_commands_module)
	bot.add_cog(CurseForge(management_portal_handler))


	@bot.event
	async def on_ready():
		logger.log_info("TitanBot has connected to Discord")
		await bot.change_presence(activity=discord.Game(name="Initializing..."), status=discord.Status.dnd)

		# Perform post-initialization for the management portal
		await management_portal_handler.post_init()

		# Check storage metadata, and perform migration as necessary
		logger.log_info("Checking guild storage metadata")
		await FileAPI.check_storage_metadata(database_version, data_migrator, bot.guilds)

		# Update local configurations and load deferred config values
		await management_portal_handler.command_handler.handle_command("update_configuration", True)
		await configuration_manager.load_deferred_configs(management_portal_handler, bot.guilds)

		# Do post-initialization for objects with a database cache
		logger.log_info("Performing post-initialization for objects with a database cache")
		await custom_commands_module.post_initialize(bot)

		# Initialize the update manager and check for updates if enabled
		update_manager = UpdateManager(management_portal_handler, configuration_manager, bot)
		if ConfigurationValues.AUTO_UPDATE_ENABLED:
			await update_manager.check_for_updates()

		# Update Osmium's import whitelist
		await osmium.set_import_whitelist(await configuration_manager.get_value("osmium_import_whitelist"))

		# Send the ready status to the management portal
		await management_portal_handler.on_ready(update_manager)

		# Set the bot status
		status_config = await configuration_manager.get_value("discord_status")
		status = await BotStatus.get_status(status_config["activity_level"], status_config["activity_text"],
											status_config["activity_url"], status_config["status_level"])
		await bot.change_presence(activity=status[0], status=status[1])
		logger.log_info("TitanBot is ready to go!")

	@bot.event
	async def on_application_command_error(ctx: discord.ApplicationContext, error: commands.CommandError):
		embed = await ErrorHandler.handle_error(error, logger)
		await ctx.respond(embed=embed)

	@bot.event
	async def on_guild_join(ctx: commands.Context):
		logger.log_info("TitanBot has joined a new guild: " + ctx.guild.name)
		logger.log_info("Updating storage metadata for new guild")
		await FileAPI.check_storage_metadata(database_version, data_migrator, bot.guilds)

		# Invalidate existing caches
		logger.log_info("Invalidating existing caches...")
		await custom_commands_module.invalidate_caches()
		# Re-initialize objects with a database cache
		await CustomCommands.post_initialize(custom_commands_module, bot)
		logger.log_info("All caches invalidated")

	def on_exit():
		GeneralUtilities.run_and_get_new_loop(ExitHandler.prepare_to_exit())

	atexit.register(on_exit)
	bot.run(ConfigurationValues.TOKEN)
