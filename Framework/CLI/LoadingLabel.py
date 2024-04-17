from textual import events
from textual.widgets import Label


class LoadingLabel(Label):

	def __init__(self, text: str, client):
		super().__init__(text, id="loading_label", classes="loading_label")
		self.client = client
		self.is_reconnecting = False

	def _on_mount(self, event: events.Mount) -> None:
		self.styles.animate("opacity", value=0, duration=2, on_complete=self.fade_in)

	async def on_idle(self) -> None:
		if self.client.is_connected:
			self.visible = False
			self.styles.width = "0%"
			self.styles.height = "0%"
		else:
			self.visible = True
			self.styles.width = "100%"
			self.styles.height = "99%"

	async def fade_out(self):
		self.styles.animate("opacity", value=0, duration=2, on_complete=self.fade_in)

	async def fade_in(self):
		self.styles.animate("opacity", value=1, duration=2, on_complete=self.fade_out)
