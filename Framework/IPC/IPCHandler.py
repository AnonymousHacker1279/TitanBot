import asyncio
import os
import socket
import threading

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.FileSystemAPI.ConfigurationManager import configuration_manager
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory
from Framework.ManagementPortal import management_portal_handler


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
				self.logger.log_info("Client disconnected (" + str(connection.getpeername()) + ")")
				self.clients.remove(connection)
				break

			# The command should be the first part of the string, split by a space.
			command_name = client_message.split(" ")[0]
			command = self.command_directory.get_command(command_name)

			# Args are everything else and should be split by spaces. Quoted strings are supported.
			args = self.__parse_args(client_message.lstrip(command_name))

			if command:
				command_instance: BasicCommand = command(management_portal_handler.bot, configuration_manager)
				response = asyncio.run_coroutine_threadsafe(command_instance.execute(args), self.loop).result(10)

				metadata: dict[str, any] = command_instance.extra_metadata.copy()

				if metadata.get("shutdown"):
					self.shutdown_flag.set()

				if command_instance.send_buffer_size != 1024:
					metadata["buffer_size"] = command_instance.send_buffer_size
				if command_instance.color != "white":
					metadata["color"] = command_instance.color

				if metadata:
					self.send_update(f"!METADATA:{metadata}")
			else:
				response = f"Unable to find command: {command_name}"

			self.send_update(response)

	def __parse_args(self, message: str) -> list[str]:
		"""Parse the arguments from a message."""
		args = []
		quote = False
		arg = ""
		for char in message:
			if char == " " and not quote:
				if arg:
					args.append(arg)
					arg = ""
			elif char == "\"":
				quote = not quote
			else:
				arg += char
		if arg:
			args.append(arg)
		return args

	def send_update(self, update: str):
		"""Send an update to all connected clients."""
		for connection in self.clients:
			connection.sendall(update.encode('utf-8'))

	def start_server(self):
		self.logger.log_info("Starting IPC server for local management connections, listening on " + ConfigurationValues.IPC_ADDRESS + ":" + str(ConfigurationValues.IPC_PORT) + "...")
		self.command_directory.load_commands()

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
