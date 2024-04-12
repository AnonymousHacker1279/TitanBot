import discord


class BasicCommand:

	def __init__(self, bot: discord.bot.Bot):
		self.bot = bot
		self.friendly_name = self.__class__.__name__.lower()
		self.send_buffer_size: int = 1024
		self.color: str = "white"

	def execute(self, args: list[str]) -> str:
		pass

	def color_text(self, text: str, color: str):
		return f"[color={color}]{text}[/color]"

	def get_color(self, percent: float):
		"""Calculate a color between green and red based on a percentage."""
		if percent < 0:
			percent = 0
		if percent > 1:
			percent = 1

		# Calculate the color
		red = int(255 * percent)
		green = int(255 * (1 - percent))
		blue = 0

		# Convert to hex and return
		return '#{:02x}{:02x}{:02x}'.format(red, green, blue)