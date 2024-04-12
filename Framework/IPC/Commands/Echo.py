import discord

from BasicCommand import BasicCommand


class Echo(BasicCommand):

	def __init__(self, bot: discord.bot.Bot):
		super().__init__(bot)
		self.friendly_name = "echo"

	def execute(self, args: list[str]) -> str:
		if args[0].startswith("color="):
			self.color = args[0].split("=")[1]
			args = args[1:]

		return "Echo: " + " ".join(args)
