import asyncio
import datetime
from enum import Enum
from multiprocessing import Queue
from queue import Empty
from threading import Thread

from Framework.FileSystemAPI import DatabaseObjects
from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.GeneralUtilities import GeneralUtilities


class LogLevel(Enum):
	"""
	Log levels are used to determine what data is logged. Set the required log level in the configuration.
	"""
	DEBUG = 0
	INFO = 1
	WARNING = 2
	ERROR = 3
	CRITICAL = 4


class ThreadedLogger:

	# There will be multiple instances of this class, so we need to make sure that
	# the log file is only opened once
	log_file_handle = None
	log_file_path = None
	log_file_lock = None

	def __init__(self, instance_name, management_portal_handler, parent_logger=None):
		self.instance_name = instance_name
		self.parent_logger = parent_logger
		self.queue = Queue()
		self.loop = asyncio.get_event_loop()
		self.thread = Thread(target=self._threaded_logger, daemon=True, name="ThreadedLogger-" + instance_name)
		self.thread.start()

		self.mph = management_portal_handler

		# If this is the first instance of this class, open the log file
		if ThreadedLogger.log_file_handle is None:
			self.open_log_file()

	def open_log_file(self):
		# Open the log file
		# The log file is stored in the bot log directory, with a name that is the current date
		logs_directory = GeneralUtilities.run_and_get(DatabaseObjects.get_log_directory())

		ThreadedLogger.log_file_path = logs_directory + "\\" + str(datetime.datetime.now().date()) + ".log"
		ThreadedLogger.log_file_handle = open(ThreadedLogger.log_file_path, "ab", buffering=0)
		ThreadedLogger.log_file_lock = asyncio.Lock()

	def close(self):
		# Close the log file
		# This method is called when the bot is shutting down
		ThreadedLogger.log_file_handle.close()

	def _threaded_logger(self):
		# This method is called in a separate thread
		# It is responsible for writing to the log file
		# It reads from the queue and writes to the log file
		# If the queue is empty, it sleeps for 1 second
		while True:
			# Get the next message from the queue
			# If the queue is empty, wait for 1 second and then try again
			# If the queue is still empty, skip this iteration and try again
			try:
				message = self.queue.get(block=True, timeout=1)
			except Empty:
				continue

			# Write the message to the console
			prepared_message = message[0] + message[1]
			print(prepared_message, end="")

			# Write the message to the log file
			asyncio.run_coroutine_threadsafe(ThreadedLogger.log_file_lock.acquire(), self.loop)
			ThreadedLogger.log_file_handle.write(prepared_message.encode())
			ThreadedLogger.log_file_handle.flush()
			# Check if it is locked before releasing it
			if ThreadedLogger.log_file_lock.locked():
				ThreadedLogger.log_file_lock.release()

			# Write the message to the management portal
			# The management portal is accessed asynchronously, so we need to run it in a separate thread
			asyncio.run_coroutine_threadsafe(self.mph.management_portal_log_data(self.instance_name, message[2].name, message[1], message[3]), self.loop)

			# If this instance has a parent logger, pass the message to it
			if self.parent_logger is not None:
				self.parent_logger.queue.put(message)

	def log(self, level: LogLevel, message: str):
		# Check if logging is enabled
		if not ConfigurationValues.LOGGING_ENABLED:
			return
		# Check the level before logging
		if ConfigurationValues.LOG_LEVEL > level.value:
			return

		message = message + "\n"

		timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
		time_block = "[" + timestamp + "] "
		source_block = "[" + self.instance_name + "/" + level.name + "]: "
		prefix_block = time_block + source_block
		self.queue.put([prefix_block, message, level, timestamp])

	def log_debug(self, message: str):
		self.log(LogLevel.DEBUG, message)

	def log_info(self, message: str):
		self.log(LogLevel.INFO, message)

	def log_warning(self, message: str):
		self.log(LogLevel.WARNING, message)

	def log_error(self, message: str):
		self.log(LogLevel.ERROR, message)

	def log_critical(self, message: str):
		self.log(LogLevel.CRITICAL, message)
