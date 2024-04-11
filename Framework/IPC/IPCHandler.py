import socket
import threading

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues
from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger


class IPCHandler:
	clients: list[socket.socket] = []

	def __init__(self):
		self.logger = ThreadedLogger("IPCHandler")

	def handle_client(self, connection: socket.socket):
		self.clients.append(connection)
		while True:
			# Receive a command from the client
			try:
				command = connection.recv(1024).decode('utf-8')
			except ConnectionResetError:
				self.logger.log_info("Client disconnected (" + str(connection.getpeername()) + ")")
				self.clients.remove(connection)
				break

			if command == 'get_log':
				# Read the log file and send its contents back to the client
				with open(self.logger.log_file_path, 'r') as f:
					log_contents = f.read()

				# Send the size of the log_contents before sending log_contents itself
				self.send_update(("[bufSize:" + str(len(log_contents)) + "]"))
				self.send_update(log_contents)
			else:
				print(f"Received command: {command}")
				# TODO: Execute the command

				# TODO: Send proper updates to the client
				update = f'Response from server: received command {command}'
				self.send_update(update)

	def send_update(self, update: str):
		"""Send an update to all connected clients."""
		for conn in self.clients:
			conn.sendall(update.encode('utf-8'))

	def start_server(self):
		self.logger.log_info("Starting IPC server for local management connections, listening on " + ConfigurationValues.IPC_ADDRESS + ":" + str(ConfigurationValues.IPC_PORT) + "...")
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((ConfigurationValues.IPC_ADDRESS, ConfigurationValues.IPC_PORT))
			s.listen()

			while True:
				# Accept new connections
				connection, address = s.accept()
				self.logger.log_info(f"New client connected to IPC server: {address}")

				# Start a new thread to handle communication with this client
				threading.Thread(target=self.handle_client, args=(connection,)).start()
