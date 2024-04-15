import json
import threading

import aiohttp
from aiohttp import ContentTypeError
from discord.ext import tasks

from Framework.ConfigurationManager import ConfigurationValues
from Framework.GeneralUtilities import GeneralUtilities
from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger
from Framework.ManagementPortal.APIEndpoints import APIEndpoints


class ManagementPortalHandler:
	bot = None
	base_data = {}
	sessions = {}
	quotes_api = None
	cf_checker_api = None
	access_control_api = None

	def __init__(self):
		self.logger = ThreadedLogger("ManagementPortalHandler")
		self.command_handler = None
		self.is_first_update_check = True
		self.initialized = False

	async def initialize(self, bot):
		"""Initialize core variables and API modules."""
		self.bot = bot
		self.base_data["bot_token"] = GeneralUtilities.generate_sha256_no_async(ConfigurationValues.TOKEN)

		self.__init_api_modules()
		self.initialized = True

	def __init_api_modules(self):
		"""Initialize extra API modules."""
		from Framework.ManagementPortal.Modules import QuotesAPI, CFCheckerAPI, AccessControlAPI

		self.quotes_api = QuotesAPI.QuotesAPI(self)
		self.cf_checker_api = CFCheckerAPI.CFCheckerAPI(self)
		self.access_control_api = AccessControlAPI.AccessControlAPI(self)

	async def get_session(self):
		thread_id = threading.get_ident()
		if thread_id not in self.sessions:
			self.sessions[thread_id] = aiohttp.ClientSession()
		return self.sessions[thread_id]

	async def close_sessions(self):
		for session in self.sessions.values():
			await session.close()

	async def post(self, endpoint: str, data: dict = None, non_management_portal=False) -> None:
		"""
		Send a POST request. Returns nothing.

		:param endpoint: The endpoint to send the request to.
		:param data: The data to send with the request.
		:param non_management_portal: If True, the request will be sent to the endpoint directly, without the management portal URL prefixed.
		"""

		if non_management_portal:
			url: str = endpoint
		else:
			url: str = ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint

		# Connect to the management portal
		session = await self.get_session()
		async with session.post(url, data=data) as response:
			# Check the response code
			await self.__check_connect_status(response.status, endpoint, non_management_portal)

	async def get(self, endpoint: str, data: dict = None, non_management_portal=False) -> dict:
		"""
		Send a GET request. Returns the response as a dictionary. If going to the management portal, it is technically a POST request since it sends auth data.

		:param endpoint: The endpoint to send the request to.
		:param data: The data to send with the request.
		:param non_management_portal: If True, the request will be sent to the endpoint directly, without the management portal URL prefixed.
		"""

		if non_management_portal:
			url: str = endpoint
		else:
			url: str = ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint

		# Connect to the management portal
		session = await self.get_session()
		if non_management_portal:

			if data:
				session.headers.update(data)

			async with session.get(url) as response:
				session.headers.clear()
				return await self.__manage_get_response(response, endpoint, non_management_portal)

		else:
			async with session.post(url, data=data) as response:
				return await self.__manage_get_response(response, endpoint, non_management_portal)

	async def __manage_get_response(self, response, endpoint: str, non_management_portal=False) -> dict | str:
		# Check the response code
		await self.__check_connect_status(response.status, endpoint, non_management_portal)

		if response.content_type == "application/json":
			try:
				return await response.json()
			except json.decoder.JSONDecodeError:
				return {}
			except ContentTypeError:
				if response.status != 401 or response.status != 403:
					self.logger.log_error(f"Unexpected content type received (expected JSON but got {response.content_type}). Response from server: {await response.text()}")
				return {}
		else:
			return await response.text()

	async def __check_connect_status(self, response_code: int, endpoint: str, non_management_portal=False):
		# If it is 401, then the parameters passed are invalid
		# If it is 403, then the bot was unable to connect, likely due to an invalid token

		if non_management_portal:
			url: str = endpoint
		else:
			url: str = ConfigurationValues.MANAGEMENT_PORTAL_URL + endpoint

		if response_code == 401:
			self.logger.log_error("Request failed: Invalid parameters")
			self.logger.log_error("Endpoint URL: " + url)
		elif response_code == 403:
			self.logger.log_error("Request failed: Failed to authenticate")
			self.logger.log_error("Endpoint URL: " + url)

	async def on_ready(self):
		self.logger.log_info("Updating management portal with bot information")

		headers = self.base_data.copy()
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

	@tasks.loop(seconds=30)
	async def update_management_portal_latency(self):
		headers = self.base_data.copy()
		try:
			headers["latency"] = str(round(self.bot.latency * 1000))
		except (OverflowError, ValueError):
			headers["latency"] = str(9999)
			self.logger.log_error(
				"Unable to update management portal latency due to an overflow error, is the bot offline?")

		await self.post(APIEndpoints.UPDATE_LATENCY, headers)

	@tasks.loop(seconds=30)
	async def check_management_portal_pending_commands(self):
		response = await self.get(APIEndpoints.CHECK_PENDING_COMMANDS, self.base_data)

		if self.command_handler is None:
			from Framework.ManagementPortal import portal_command_handler
			self.command_handler = portal_command_handler

		await self.command_handler.parse_pending_commands(response)
