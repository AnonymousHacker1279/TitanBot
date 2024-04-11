import json

import aiohttp
from aiohttp import ContentTypeError
from discord.ext import tasks

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.ManagementPortal.APIEndpoints import APIEndpoints
from GeneralUtilities import GeneralUtilities


class ManagementPortalHandler:
	bot = None
	base_headers = {}
	quotes_api = None
	cf_checker_api = None
	access_control_api = None

	def __init__(self):
		self.logger = ThreadedLogger("ManagementPortalHandler")
		self.command_handler = None
		self.update_manager = None
		self.is_first_update_check = True

	def initialize(self, bot):
		"""Initialize core variables and API modules."""
		self.bot = bot
		self.base_headers["bot_token"] = GeneralUtilities.generate_sha256_no_async(ConfigurationValues.TOKEN)

		self.__init_api_modules()

	def __init_api_modules(self):
		"""Initialize extra API modules."""
		from Framework.ManagementPortal.Modules import mp_quotes_api, mp_cf_checker_api, mp_access_control_api

		self.quotes_api = mp_quotes_api
		self.cf_checker_api = mp_cf_checker_api
		self.access_control_api = mp_access_control_api

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
				except ContentTypeError:
					if response.status != 401 or response.status != 403:
						self.logger.log_error(f"Unexpected content type received (expected JSON but got {response.content_type}). Response from server: {await response.text()}")
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
		self.cf_checker_api.check_for_updates.start()

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

		if self.command_handler is None:
			from Framework.ManagementPortal import portal_command_handler
			self.command_handler = portal_command_handler

		await self.command_handler.parse_pending_commands(response)

	@tasks.loop(seconds=86400)
	async def check_for_updates(self):
		# The first check is ignored because this loop runs immediately on setup
		# and the bot already checks on initialization
		if self.is_first_update_check:
			self.is_first_update_check = False
			return

		await self.update_manager.check_for_updates()
