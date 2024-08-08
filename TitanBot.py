import asyncio
import concurrent.futures
import os
import subprocess
import sys
import threading
import time

import discord
from discord.ext import commands

from Framework.CommandGroups.CurseForge import CurseForge
from Framework.CommandGroups.Debugging import Debugging
from Framework.CommandGroups.Fun import Fun
from Framework.CommandGroups.Genius import Genius
from Framework.CommandGroups.Help import Help
from Framework.CommandGroups.Quotes import Quotes
from Framework.CommandGroups.Statistics import Statistics
from Framework.CommandGroups.Utility import Utility
from Framework.ConfigurationManager import BotStatus, ConfigurationValues
from Framework.GeneralUtilities import ErrorHandler
from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger
from Framework.IPC import ipc_handler
from Framework.ManagementPortal import management_portal_handler


def start_watch_for_shutdown(loop: asyncio.AbstractEventLoop):
	asyncio.set_event_loop(loop)
	loop.run_until_complete(watch_for_shutdown())


shutdown_loop = asyncio.new_event_loop()
executor = concurrent.futures.ThreadPoolExecutor()


if __name__ == "__main__":

	ConfigurationValues.VERSION = "v3.0.0-indev"
	ConfigurationValues.COMMIT = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()

	intents = discord.Intents.all()
	bot = discord.Bot(intents=intents)
	bot.help_command = Help()

	# Perform initialization for the management portal
	asyncio.run(management_portal_handler.initialize(bot))
	ThreadedLogger.initialize(management_portal_handler)

	logger = ThreadedLogger("TitanBot")
	logger.log_info("TitanBot " + ConfigurationValues.VERSION + " @ " + ConfigurationValues.COMMIT + " starting up")
	logger.log_info("Running on Python " + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]))

	cogs = [
		Quotes(),
		Fun(),
		Utility(),
		Genius(),
		CurseForge(),
		Debugging(),
		Statistics()
	]

	for cog in cogs:
		bot.add_cog(cog)

	# Purge the temporary file directory
	path = f"{os.getcwd()}/Storage/Temp"
	temp_file_count = 0
	for file in os.listdir(path):
		logger.log_debug(f"Removing temporary file: {file}")
		os.remove(f"{path}/{file}")
		temp_file_count += 1
	logger.log_info(f"Removed {temp_file_count} temporary files")

	@bot.event
	async def on_ready():
		logger.log_info("TitanBot has connected to Discord")
		await bot.change_presence(activity=discord.CustomActivity(name="Initializing..."), status=discord.Status.dnd)

		# Update local configurations and load deferred config values
		logger.log_info("Loading configuration data from the management portal")
		from Framework.ConfigurationManager import configuration_manager
		await configuration_manager.load_deferred_configs(bot.guilds)

		# Perform post-init tasks for each cog
		for cog in cogs:
			await cog.post_init()

		await management_portal_handler.on_ready()

		# Set the bot status
		status = await BotStatus.get_status_from_config(configuration_manager)
		await bot.change_presence(activity=status[0], status=status[1])

		# Start the IPC server
		threading.Thread(target=ipc_handler.start_server, daemon=True).start()

		executor.submit(start_watch_for_shutdown, shutdown_loop)

		logger.log_info("TitanBot is ready to go!")

	@bot.event
	async def on_application_command_error(ctx: discord.ApplicationContext, error: commands.CommandError):
		embed = await ErrorHandler.handle_error(error, logger)
		await ctx.respond(embed=embed)

	async def watch_for_shutdown():
		# Monitor for shutdown events over IPC
		while True:
			if ipc_handler.shutdown_flag.is_set():
				ThreadedLogger.shutdown = True
				await management_portal_handler.update_management_portal_latency.stop()
				await management_portal_handler.cf_checker_api.check_for_updates.stop()
				await management_portal_handler.close_sessions()
				await bot.close()
				break

			time.sleep(1)

	bot.run(ConfigurationValues.TOKEN)
