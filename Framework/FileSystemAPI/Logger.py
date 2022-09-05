import datetime
import os.path
from enum import Enum
from pathlib import Path

from Framework.FileSystemAPI import DatabaseObjects
from Framework.GeneralUtilities import Constants, GeneralUtilities


class Logger:

	def __init__(self, source: str):
		self.source = source

	async def log_debug(self, message: str):
		await self.log(LogLevel.DEBUG, message)

	async def log_info(self, message: str):
		await self.log(LogLevel.INFO, message)

	async def log_warning(self, message: str):
		await self.log(LogLevel.WARNING, message)

	async def log_error(self, message: str):
		await self.log(LogLevel.ERROR, message)

	async def log_critical(self, message: str):
		await self.log(LogLevel.CRITICAL, message)

	async def log(self, level, message: str):
		# Check the level before logging
		if Constants.LOG_LEVEL > level.value:
			return

		# Prepare log with time and source
		time_block = "[" + str(datetime.datetime.now()) + "] "
		source_block = "[" + self.source + "/" + level.name + "]: "
		log = time_block + source_block + message

		# File path
		path = await DatabaseObjects.get_log_directory() + "\\" + str(datetime.datetime.now().date()) + ".log"

		# Log data to console
		print(log)
		# Log data to file
		output_file = Path(path)
		output_file.parent.mkdir(exist_ok=True, parents=True)

		log_location = os.path.abspath(path)
		with open(log_location, "a") as log_file:
			log_file.write(log + "\n")
			log_file.close()


class LogLevel(Enum):
	"""
	Log levels are used to determine what data is logged. Set the required log level in the config file.
	"""
	DEBUG = 0
	INFO = 1
	WARNING = 2
	ERROR = 3
	CRITICAL = 4
