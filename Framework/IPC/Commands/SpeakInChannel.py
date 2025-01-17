import discord

from Framework.ConfigurationManager import ConfigurationManager
from Framework.IPC.BasicCommand import BasicCommand
from Framework.IPC.CommandDirectory import CommandDirectory


class SpeakInChannel(BasicCommand):

	def __init__(self, bot: discord.bot.Bot, config_manager: ConfigurationManager, command_directory: CommandDirectory):
		super().__init__(bot, config_manager, command_directory)
		self.friendly_name = "speak_in_channel"
		self.is_recursive = True
		self.channel = None

	async def execute(self, args: list[str]) -> str:
		if not args:
			return "No arguments provided."

		if args[0] == "exit":
			self.command_context = ""
			self.is_recursive = False
			return "Session ended."

		if self.command_context == "" and len(args) < 2:
			return "Not enough arguments provided."
		else:
			if self.channel is None:
				try:
					self.channel = self.bot.get_channel(int(args[0]))
				except ValueError:
					return "Invalid channel ID."

				if not self.channel:
					return "Channel not found."

				message = " ".join(args[1:])
			else:
				message = " ".join(args)

		await self.channel.send(message)
		self.command_context = f"Speaking in {self.channel.guild.name}/{self.channel.name}"

		return f"Message sent to {self.channel.guild.name}/{self.channel.name}."

	async def get_help_message(self) -> str:
		msg = """
		Start a chat session with the provided channel ID. Allows messages to be sent to the server
		as the bot. This will not display incoming messages in the channel. Upon starting a session, 
		enter 'exit' to end the session.
		""".replace("\t", "")
		args = {
			"channel_id": {
				"description": "The ID of the destination channel.",
				"arguments": {
					"message": {
						"description": "The message to send to the channel.",
						"arguments": {}
					},
				}
			}
		}

		return await self.format_help_message(msg, args)
