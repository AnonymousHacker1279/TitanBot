import os
import threading

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Input

from Framework.CLI.IPCClient import IPCClient
from Framework.CLI.TBHighlighter import TBHighlighter


def load_config() -> tuple[str, int]:
	"""Load configuration values."""
	load_dotenv()
	return os.getenv("IPC_ADDRESS"), int(os.getenv("IPC_PORT"))


class TitanBotApp(App):
	"""A Textual app providing access over IPC calls to TitanBot, allowing for management without keeping the original terminal open."""

	BINDINGS = [("e", "exit", "Exit")]
	CSS_PATH = "Framework/CLI/app.tcss"

	version = "v1.0.0"

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.ipc_address = load_config()

		self.client = IPCClient(self.ipc_address)

		self.rich_log_widget = RichLog(highlight=True)
		self.rich_log_widget.highlighter = TBHighlighter()

		self.command_input_widget = Input(placeholder="Enter a command...")

	def on_mount(self) -> None:
		"""Connect to the IPC server and start a thread to receive updates."""
		self.client.connect()
		threading.Thread(target=self.receive_updates, name="IPC Listener").start()

	def compose(self) -> ComposeResult:
		"""Create child widgets."""
		yield Header(show_clock=True)
		yield self.rich_log_widget
		yield self.command_input_widget
		yield Footer()

	async def on_input_submitted(self, message: Input.Submitted):
		"""Send commands to the IPC server."""
		if message.value == "clear":
			self.rich_log_widget.clear()
		else:
			# Write the command to the log
			self.rich_log_widget.write(">>> " + message.value)
			await self.client.send(message.value)

		self.command_input_widget.clear()

	def action_exit(self) -> None:
		"""An action to exit the app."""
		self.client.close()
		self.exit()

	def receive_updates(self):
		while True:
			try:
				update = self.client.recv()
			except ConnectionResetError:
				self.app.exit(message="Connection to TitanBot lost.")
				break

			if update:
				if update.startswith("!METADATA:"):
					buffer_size = 1024
					metadata: dict[str, any] = eval(update[10:])
					if "shutdown" in metadata:
						self.client.close()
						self.app.exit(message="TitanBot is shutting down.")
						break
						
					if "buffer_size" in metadata:
						buffer_size = metadata["buffer_size"]
					if "color" in metadata:
						self.rich_log_widget.highlighter.color_of_next_entry = metadata["color"]
					update = self.client.recv(buffer_size)

				self.rich_log_widget.write(update)


if __name__ == "__main__":
	app = TitanBotApp()
	app.title = "TitanBot Management (CLI) @ " + app.ipc_address[0] + ":" + str(app.ipc_address[1])
	app.sub_title = app.version
	app.run()
