import os
import socket
import threading

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory
from Framework.ManagementPortal import management_portal_handler


class IPCHandler:
	clients: list[socket.socket] = []

	def __init__(self):
		self.logger = ThreadedLogger("IPCHandler")
		self.command_directory = CommandDirectory(os.getcwd() + "/Framework/IPC/Commands")

	def handle_client(self, connection: socket.socket):
		self.clients.append(connection)
		while True:
			try:
				client_message = connection.recv(1024).decode('utf-8')
			except ConnectionResetError:
				self.logger.log_info("Client disconnected (" + str(connection.getpeername()) + ")")
				self.clients.remove(connection)
				break

			# The command should be the first part of the string, split by spaces. Everything else is an arg
			client_message = client_message.split(" ")

			command = self.command_directory.get_command(client_message[0])
			args = client_message[1:]

			if command:
				command_instance: BasicCommand = command(management_portal_handler.bot)
				response = command_instance.execute(args)

				metadata: dict[str, any] = {}

				if command_instance.send_buffer_size != 1024:
					metadata["buffer_size"] = command_instance.send_buffer_size
				if command_instance.color != "white":
					metadata["color"] = command_instance.color

				if metadata:
					self.send_update(f"!METADATA:{metadata}")
			else:
				response = f"Unable to find command: {client_message[0]}"

			self.send_update(response)

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
				# Accept new connections
				connection, address = s.accept()
				self.logger.log_info(f"New client connected to IPC server: {address}")

				# Start a new thread to handle communication with this client
				threading.Thread(target=self.handle_client, args=(connection,)).start()
