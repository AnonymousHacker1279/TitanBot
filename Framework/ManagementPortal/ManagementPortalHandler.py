import json
from enum import Enum

import requests
from discord.ext import tasks

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.GeneralUtilities import GeneralUtilities
from Framework.ManagementPortal.PortalCommandHandler import PortalCommandHandler


class ManagementPortalHandler:

	def __init__(self, bot, configuration_manager):
		self.bot = bot
		self.cm = configuration_manager
		self.logger = ThreadedLogger("ManagementPortalHandler", self)
		self.command_handler = PortalCommandHandler(self)
		self.update_manager = None
		self.is_first_update_check = True
		self.base_headers = {
			'bot_token': GeneralUtilities.generate_sha256_no_async(ConfigurationValues.TOKEN)
		}

	async def __post(self, endpoint, headers: dict = None):
		# Connect to the management portal
		response = requests.post(ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint, data=headers)
		# Check the response code
		await self.__check_connect_status(response.status_code, endpoint)

	async def __get(self, endpoint, headers: dict = None) -> dict:
		# Connect to the management portal
		response = requests.post(ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint, data=headers)
		# Check the response code
		await self.__check_connect_status(response.status_code, endpoint)

		return response.json()

	async def __check_connect_status(self, response_code: int, endpoint: str):
		# If it is 401, then the parameters passed are invalid
		# If it is 403, then the bot was unable to connect, likely due to an invalid token
		if response_code == 401:
			self.logger.log_error("Unable to connect to the management portal: Invalid parameters")
			self.logger.log_error("Endpoint URL: " + ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint)
		elif response_code == 403:
			self.logger.log_error("Unable to connect to the management portal: Failed to authenticate")
			self.logger.log_error("Endpoint URL: " + ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint)

	async def on_ready(self, update_manager):
		self.logger.log_info("Updating management portal with bot information")
		headers = self.base_headers.copy()
		# Make a dictionary of all the guilds and their IDs
		guilds = {}
		for guild in self.bot.guilds:
			guilds[guild.id] = guild.name
		headers["guilds"] = json.dumps(guilds)
		headers["version"] = ConfigurationValues.VERSION

		await self.__post(APIEndpoints.READY, headers)
		self.update_management_portal_latency.start()
		self.check_management_portal_pending_commands.start()

		self.update_manager = update_manager
		if ConfigurationValues.AUTO_UPDATE_ENABLED:
			self.check_for_updates.change_interval(seconds=ConfigurationValues.UPDATE_CHECK_FREQUENCY)
			self.check_for_updates.start()

	@tasks.loop(seconds=30)
	async def update_management_portal_latency(self):
		headers = self.base_headers.copy()
		try:
			headers["latency"] = str(round(self.bot.latency * 1000))
		except OverflowError:
			headers["latency"] = str(9999)
			self.logger.log_error("Unable to update management portal latency due to an overflow error, is the bot offline?")

		await self.__post(APIEndpoints.UPDATE_LATENCY, headers)

	@tasks.loop(seconds=30)
	async def check_management_portal_pending_commands(self):
		response = await self.__get(APIEndpoints.CHECK_PENDING_COMMANDS, self.base_headers)
		await self.command_handler.parse_pending_commands(response)

	@tasks.loop(seconds=86400)
	async def check_for_updates(self):
		# The first check is ignored because this loop runs immediately on setup
		# and the bot already checks on initialization
		if self.is_first_update_check:
			self.is_first_update_check = False
			return

		await self.update_manager.check_for_updates()

	async def update_management_portal_command_completed(self, command: str):
		headers = self.base_headers.copy()
		headers["command"] = command

		await self.__post(APIEndpoints.UPDATE_COMMAND_COMPLETED, headers)

	async def get_management_portal_configuration(self, file_name: str) -> dict:
		headers = self.base_headers.copy()
		headers["name"] = file_name
		return await self.__get(APIEndpoints.GET_CONFIGURATION, headers)

	async def update_management_portal_command_used(self, module_name: str, command_name: str, guild_id: int):
		headers = self.base_headers.copy()
		headers["module_name"] = module_name
		headers["command_name"] = command_name
		headers["guild_id"] = str(guild_id)

		await self.__post(APIEndpoints.UPDATE_COMMAND_USED, headers)

	async def management_portal_log_data(self, source: str, level: str, message: str, timestamp: str):
		headers = self.base_headers.copy()
		headers["source"] = source
		headers["log_level"] = level
		headers["message"] = message
		headers["timestamp"] = timestamp

		await self.__post(APIEndpoints.LOG_DATA, headers)


class APIEndpoints(str, Enum):
	READY = "/bot_ready.php"
	UPDATE_LATENCY = "/bot_update_latency.php"
	UPDATE_COMMAND_USED = "/bot_update_command_used.php"
	LOG_DATA = "/bot_log_data.php"
	CHECK_PENDING_COMMANDS = "/bot_check_pending_commands.php"
	UPDATE_COMMAND_COMPLETED = "/bot_update_command_completed.php"
	GET_CONFIGURATION = "/configurations/portal_get_configuration.php"
