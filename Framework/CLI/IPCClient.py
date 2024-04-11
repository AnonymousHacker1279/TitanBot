import socket


class IPCClient:
	def __init__(self, server):
		self.server = server
		self.socket = None

	async def connect(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect(self.server)

	async def send(self, data):
		self.socket.sendall(data.encode('utf-8'))

	def recv(self, buffer_size: int = 1024):
		return self.socket.recv(buffer_size).decode('utf-8')

	def close(self):
		self.socket.close()
