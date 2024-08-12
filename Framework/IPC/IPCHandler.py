import asyncio
import os
import socket
import threading

import discord

from Framework.ConfigurationManager import ConfigurationValues
from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger
from Framework.IPC.CommandDirectory import CommandDirectory


class IPCHandler:
	clients: list[socket.socket] = []
	shutdown_flag = threading.Event()

	def __init__(self):
		self.logger = ThreadedLogger("IPCHandler")
		self.command_directory = CommandDirectory(os.getcwd() + "/Framework/IPC/Commands")
		self.loop = asyncio.get_event_loop()

	def handle_client(self, connection: socket.socket):
		self.clients.append(connection)
		while True:
			if self.shutdown_flag.is_set():
				break

			try:
				client_message = connection.recv(1024).decode('utf-8')
			except ConnectionResetError:
				self.logger.log_info("Client disconnected " + str(connection.getpeername()))
				self.clients.remove(connection)
				break

			# The command should be the first part of the string, split by a space.
			command_name = client_message.split(" ")[0]
			command = self.command_directory.get_command(command_name)

			# Args are everything else and should be split by spaces. Quoted strings are supported.
			args = self.__parse_args(client_message.lstrip(command_name))

			if command:
				try:
					# Important to check if the loop is running here
					if self.loop.is_running():
						# This will work when outside a debugging environment but deadlock inside one
						response = asyncio.run_coroutine_threadsafe(command.execute(args), self.loop).result()
					else:
						# This will work when debugging but crash outside a debugging environment
						response = self.loop.run_until_complete(command.execute(args))
				except Exception as e:
					response = f"An error occurred while executing the command. Details:\n{e}"
					self.logger.log_error(f"An error occurred while executing the command. Details:\n{e}")

				metadata: dict[str, any] = command.extra_metadata.copy()

				if metadata.get("shutdown"):
					self.shutdown_flag.set()

				if command.send_buffer_size != 1024:
					metadata["buffer_size"] = command.send_buffer_size
				if command.color != "white":
					metadata["color"] = command.color

				if metadata:
					self.send_update(f"!METADATA:{metadata}")
			else:
				response = f"Unable to find command: {command_name}"

			if response is not None:
				self.send_update(response)

	def __parse_args(self, message: str) -> list[any]:
		"""Parse the arguments from a message."""
		raw_args = []
		quote = False
		arg = ""
		for char in message:
			if char == " " and not quote:
				if arg:
					raw_args.append(arg)
					arg = ""
			elif char == "\"":
				quote = not quote
			else:
				arg += char

		if arg:
			raw_args.append(arg)

		proper_args = []
		for arg in raw_args:
			# Check if the argument is a type other than a string
			arg = self.__check_arg_type(arg)
			# Check for list-type elements, and properly convert them to list objects
			if isinstance(arg, str) and arg.startswith("[") and arg.endswith("]"):
				# Remove the brackets and split the elements by comma
				list_elements = arg[1:-1].split(",")
				# Strip whitespace and check the type of each element
				list_elements = [self.__check_arg_type(element.strip()) for element in list_elements]
				arg = list_elements

			proper_args.append(arg)

		return proper_args

	def __check_arg_type(self, arg: str) -> any:
		"""Check an argument type, in case it is anything other than string."""
		if arg.lower() == "true":
			arg = True
		elif arg.lower() == "false":
			arg = False
		elif arg.isdigit():
			arg = int(arg)

		return arg

	def send_update(self, update: str):
		"""Send an update to all connected clients."""
		for connection in self.clients:
			connection.sendall(update.encode('utf-8'))

	def start_server(self, bot: discord.Bot):
		self.logger.log_info("Starting IPC server for local management connections, listening on " + ConfigurationValues.IPC_ADDRESS + ":" + str(
			ConfigurationValues.IPC_PORT) + "...")
		self.command_directory.load_commands(bot)

		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((ConfigurationValues.IPC_ADDRESS, ConfigurationValues.IPC_PORT))
			s.listen()

			while True:
				if self.shutdown_flag.is_set():
					break

				# Accept new connections
				connection, address = s.accept()
				self.logger.log_info(f"New client connected to IPC server: {address}")

				# Start a new thread to handle communication with this client
				threading.Thread(target=self.handle_client, args=(connection,)).start()

			# Close all client connections
			for client in self.clients:
				client.close()
