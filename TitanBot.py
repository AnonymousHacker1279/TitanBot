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
from Framework.ConfigurationManager import configuration_manager
from Framework.GeneralUtilities import ErrorHandler
from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger
from Framework.IPC import ipc_handler


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

	ThreadedLogger.initialize()

	logger = ThreadedLogger("TitanBot")
	logger.log_info("TitanBot " + ConfigurationValues.VERSION + " @ " + ConfigurationValues.COMMIT + " starting up")
	logger.log_info("Running on Python " + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]))

	cogs = [
		Quotes(bot, configuration_manager),
		Fun(bot, configuration_manager),
		Utility(bot, configuration_manager),
		Genius(bot, configuration_manager),
		CurseForge(bot, configuration_manager),
		Debugging(bot, configuration_manager),
		Statistics(bot, configuration_manager)
	]

	for cog in cogs:
		bot.add_cog(cog)

	# Purge the temporary file directory
	path = f"{os.getcwd()}/Storage/Temp"
	temp_file_count = 0
	try:
		for file in os.listdir(path):
			logger.log_debug(f"Removing temporary file: {file}")
			os.remove(f"{path}/{file}")
			temp_file_count += 1
		logger.log_info(f"Removed {temp_file_count} temporary files")
	except FileNotFoundError:
		# Create the directory
		os.makedirs(path)

	@bot.event
	async def on_ready():
		logger.log_info("TitanBot has connected to Discord")
		await bot.change_presence(activity=discord.CustomActivity(name="Initializing..."), status=discord.Status.dnd)

		# Update local configurations
		logger.log_info("Loading configuration data...")
		configuration_manager.bot = bot
		await configuration_manager.load_deferred_configs(bot.guilds)

		# Perform post-init tasks for each cog
		for cog in cogs:
			await cog.post_init()

		# Set the bot status
		status = await BotStatus.get_status_from_config(configuration_manager)
		await bot.change_presence(activity=status[0], status=status[1])

		# Start the IPC server
		threading.Thread(target=ipc_handler.start_server, args=[bot], daemon=True).start()

		executor.submit(start_watch_for_shutdown, shutdown_loop)

		logger.log_info("TitanBot is ready to go!")

	@bot.event
	async def on_application_command_error(ctx: discord.ApplicationContext, error: commands.CommandError):
		embed = await ErrorHandler.handle_error(ctx, error, logger)
		await ctx.respond(embed=embed)

	async def watch_for_shutdown():
		# Monitor for shutdown events over IPC
		while True:
			if ipc_handler.shutdown_flag.is_set():
				ThreadedLogger.shutdown = True
				await cogs[5].check_for_updates.stop()  # CF update checker
				await bot.close()
				break

			time.sleep(1)

	bot.run(ConfigurationValues.TOKEN)
