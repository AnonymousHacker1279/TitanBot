import sys
import threading

import discord
from discord.ext import commands

from Framework.CommandGroups.AccessControl import AccessControl
from Framework.CommandGroups.CurseForge import CurseForge
from Framework.CommandGroups.Debugging import Debugging
from Framework.CommandGroups.Fun import Fun
from Framework.CommandGroups.Genius import Genius
from Framework.CommandGroups.Help import Help
from Framework.CommandGroups.Quotes import Quotes
from Framework.CommandGroups.Utility import Utility
from Framework.FileSystemAPI import FileAPI
from Framework.FileSystemAPI.ConfigurationManager import BotStatus, ConfigurationValues
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.FileSystemAPI.UpdateManager.UpdateManager import UpdateManager
from Framework.GeneralUtilities import ErrorHandler, GeneralUtilities
from Framework.IPC import ipc_handler
from Framework.ManagementPortal import management_portal_handler

if __name__ == "__main__":

	ConfigurationValues.VERSION = "v3.0.0-indev"
	ConfigurationValues.COMMIT = GeneralUtilities.get_git_revision_short_hash()

	intents = discord.Intents.all()
	bot = discord.Bot(intents=intents)
	bot.help_command = Help()

	# Perform initialization for the management portal
	management_portal_handler.initialize(bot)
	ThreadedLogger.initialize(management_portal_handler)

	FileAPI.initialize()

	logger = ThreadedLogger("TitanBot")
	logger.log_info("TitanBot " + ConfigurationValues.VERSION + " @ " + ConfigurationValues.COMMIT + " starting up")
	logger.log_info("Running on Python " + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]))

	bot.add_cog(Quotes())
	bot.add_cog(Fun())
	bot.add_cog(Utility())
	bot.add_cog(Genius())
	bot.add_cog(AccessControl())
	bot.add_cog(CurseForge())
	bot.add_cog(Debugging())


	@bot.event
	async def on_ready():
		logger.log_info("TitanBot has connected to Discord")
		await bot.change_presence(activity=discord.CustomActivity(name="Initializing..."), status=discord.Status.dnd)

		# Update local configurations and load deferred config values
		logger.log_info("Loading configuration data from the management portal")
		from Framework.FileSystemAPI.ConfigurationManager import configuration_manager
		await configuration_manager.load_deferred_configs(bot.guilds)

		# Initialize the update manager and check for updates if enabled
		update_manager = UpdateManager(configuration_manager, bot)
		if ConfigurationValues.AUTO_UPDATE_ENABLED:
			await update_manager.check_for_updates()

		# Send the ready status to the management portal
		await management_portal_handler.on_ready(update_manager)

		# Set the bot status
		status_config = await configuration_manager.get_value("discord_status")
		status = await BotStatus.get_status(status_config["activity_level"], status_config["activity_text"],
											status_config["activity_url"], status_config["activity_emoji"],
											status_config["status_level"])
		await bot.change_presence(activity=status[0], status=status[1])

		# Start the IPC server
		threading.Thread(target=ipc_handler.start_server).start()

		logger.log_info("TitanBot is ready to go!")

	@bot.event
	async def on_application_command_error(ctx: discord.ApplicationContext, error: commands.CommandError):
		embed = await ErrorHandler.handle_error(error, logger)
		await ctx.respond(embed=embed)

	bot.run(ConfigurationValues.TOKEN)
