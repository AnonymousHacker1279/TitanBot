import json
import threading

import aiohttp
from aiohttp import ContentTypeError
from discord import Bot

from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger


class WebRequestHandler:
	bot: Bot = None
	sessions = {}

	def __init__(self):
		self.logger = ThreadedLogger("WebRequestHandler")
		self.command_handler = None

	async def get_session(self) -> aiohttp.ClientSession:
		"""Get a session for the current thread."""
		thread_id = threading.get_ident()
		if thread_id not in self.sessions:
			self.sessions[thread_id] = aiohttp.ClientSession()
		return self.sessions[thread_id]

	async def close_sessions(self) -> None:
		"""Close all sessions."""
		for session in self.sessions.values():
			await session.close()

	async def post(self, endpoint: str, data: dict = None) -> None:
		"""
		Send a POST request. Returns nothing.

		:param endpoint: The endpoint to send the request to.
		:param data: The data to send with the request.
		"""

		session = await self.get_session()
		async with session.post(endpoint, data=data) as response:
			# Check the response code
			await self.__check_connect_status(response.status, endpoint)

	async def get(self, endpoint: str, data: dict = None) -> dict | str:
		"""
		Send a GET request. Returns the response as a dictionary.

		:param endpoint: The endpoint to send the request to.
		:param data: The data to send with the request.
		"""

		session = await self.get_session()
		if data:
			session.headers.update(data)

		async with session.get(endpoint) as response:
			session.headers.clear()
			return await self.__manage_get_response(response, endpoint)

	async def __manage_get_response(self, response: aiohttp.ClientResponse, endpoint: str) -> dict | str:
		"""
		Manage the response of a GET request.

		:param response: The response from the request.
		:param endpoint: The endpoint the request was sent to.
		"""

		await self.__check_connect_status(response.status, endpoint)

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

	async def __check_connect_status(self, response_code: int, endpoint: str) -> None:
		"""
		Check the connection status by the response code and log any errors.

		:param response_code: The response code from the request.
		:param endpoint: The endpoint the request was sent to.
		"""

		if response_code == 401:
			self.logger.log_error("Request failed: Invalid parameters")
			self.logger.log_error("Endpoint URL: " + endpoint)
		elif response_code == 403:
			self.logger.log_error("Request failed: Failed to authenticate")
			self.logger.log_error("Endpoint URL: " + endpoint)
