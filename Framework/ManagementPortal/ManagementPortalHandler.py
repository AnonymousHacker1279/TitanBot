import json

import aiohttp
from discord.ext import tasks

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.GeneralUtilities import GeneralUtilities
from Framework.ManagementPortal.APIEndpoints import APIEndpoints
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

		self.quotes = None
		self.data_migration = None
		self.cf_checker = None

	async def post_init(self):
		from Framework.ManagementPortal.Modules.DataMigrationAPI import DataMigrationAPI
		from Framework.ManagementPortal.Modules.QuotesAPI import QuotesAPI
		from Framework.ManagementPortal.Modules.CFCheckerAPI import CFCheckerAPI

		# Define API modules
		self.data_migration = DataMigrationAPI(self.bot, self.cm)
		self.quotes = QuotesAPI(self.bot, self.cm)
		self.cf_checker = CFCheckerAPI(self.bot, self.cm)

	async def post(self, endpoint, headers: dict = None):
		"""Send a POST request to the management portal."""

		# Connect to the management portal
		async with aiohttp.ClientSession() as session:
			async with session.post(ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint, data=headers) as response:
				# Check the response code
				await self.__check_connect_status(response.status, endpoint)

	async def get(self, endpoint, headers: dict = None) -> dict:
		"""Send a POST request to the management portal, but returns a JSON response."""

		# Connect to the management portal
		async with aiohttp.ClientSession() as session:
			async with session.post(ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint, data=headers) as response:
				# Check the response code
				await self.__check_connect_status(response.status, endpoint)

				try:
					return await response.json()
				except json.decoder.JSONDecodeError:
					return {}

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

		await self.post(APIEndpoints.READY, headers)

		self.update_management_portal_latency.start()
		self.check_management_portal_pending_commands.start()
		self.check_for_cf_project_updates.start()

		self.update_manager = update_manager
		if ConfigurationValues.AUTO_UPDATE_ENABLED:
			self.check_for_updates.change_interval(seconds=ConfigurationValues.UPDATE_CHECK_FREQUENCY)
			self.check_for_updates.start()

	@tasks.loop(seconds=30)
	async def update_management_portal_latency(self):
		headers = self.base_headers.copy()
		try:
			headers["latency"] = str(round(self.bot.latency * 1000))
		except (OverflowError, ValueError):
			headers["latency"] = str(9999)
			self.logger.log_error("Unable to update management portal latency due to an overflow error, is the bot offline?")

		await self.post(APIEndpoints.UPDATE_LATENCY, headers)

	@tasks.loop(seconds=30)
	async def check_management_portal_pending_commands(self):
		response = await self.get(APIEndpoints.CHECK_PENDING_COMMANDS, self.base_headers)
		await self.command_handler.parse_pending_commands(response)

	@tasks.loop(seconds=86400)
	async def check_for_updates(self):
		# The first check is ignored because this loop runs immediately on setup
		# and the bot already checks on initialization
		if self.is_first_update_check:
			self.is_first_update_check = False
			return

		await self.update_manager.check_for_updates()

	@tasks.loop(seconds=600)
	async def check_for_cf_project_updates(self):
		await self.cf_checker.check_for_updates()

	async def update_management_portal_command_completed(self, command: str):
		headers = self.base_headers.copy()
		headers["command"] = command

		await self.post(APIEndpoints.UPDATE_COMMAND_COMPLETED, headers)

	async def get_management_portal_configuration(self, file_name: str) -> dict:
		headers = self.base_headers.copy()
		headers["name"] = file_name
		return await self.get(APIEndpoints.GET_CONFIGURATION, headers)

	async def update_management_portal_command_used(self, module_name: str, command_name: str, guild_id: int):
		headers = self.base_headers.copy()
		headers["module_name"] = module_name
		headers["command_name"] = command_name
		headers["guild_id"] = str(guild_id)

		await self.post(APIEndpoints.UPDATE_COMMAND_USED, headers)

	async def management_portal_log_data(self, source: str, level: str, message: str, timestamp: str):
		headers = self.base_headers.copy()
		headers["source"] = source
		headers["log_level"] = level
		headers["message"] = message
		headers["timestamp"] = timestamp

		await self.post(APIEndpoints.LOG_DATA, headers)
