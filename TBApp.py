import os
import threading

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, RichLog, Input

from Framework.CLI.IPCClient import IPCClient
from Framework.CLI.LogHighlighter import LogHighlighter
from Framework.GeneralUtilities import GeneralUtilities


def load_config() -> tuple[str, int]:
	"""Load configuration values."""
	load_dotenv()
	return os.getenv("IPC_ADDRESS"), int(os.getenv("IPC_PORT"))


class TitanBotApp(App):
	"""A Textual app providing access over IPC calls to TitanBot, allowing for management without keeping the original terminal open."""

	BINDINGS = [("e", "exit", "Exit")]
	CSS_PATH = "Framework/CLI/app.tcss"

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.ipc_address = load_config()

		self.client = IPCClient(self.ipc_address)
		self.rich_log_widget = RichLog(highlight=True)
		self.rich_log_widget.highlighter = LogHighlighter()
		self.command_input_widget = Input(placeholder="Enter a command...")

	def on_mount(self) -> None:
		"""Connect to the IPC server and start a thread to receive updates."""
		GeneralUtilities.run_and_get(self.client.connect())
		threading.Thread(target=self.receive_updates).start()

	def compose(self) -> ComposeResult:
		"""Create child widgets."""
		yield Header(show_clock=True)
		yield self.rich_log_widget
		yield self.command_input_widget
		yield Footer()

	async def on_input_submitted(self, message: Input.Submitted):
		"""Send commands to the IPC server."""
		await self.client.send(message.value)
		self.command_input_widget.clear()

	def action_exit(self) -> None:
		"""An action to exit the app."""
		self.client.close()
		self.exit()

	def receive_updates(self):
		while True:
			update = self.client.recv()
			if update:
				if update.startswith("[bufSize:"):
					buf_size = int(update[9:-1])
					update = self.client.recv(buf_size)
				self.rich_log_widget.write(update)


if __name__ == "__main__":
	app = TitanBotApp()
	app.title = "TitanBot Management"
	app.run()
