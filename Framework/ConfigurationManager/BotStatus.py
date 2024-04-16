from typing import Union

import discord

from Framework.ConfigurationManager import ConfigurationManager


async def get_status_from_config(configuration_manager: ConfigurationManager) -> tuple[Union[discord.Game, discord.Streaming, discord.Activity, discord.CustomActivity], discord.Status]:
	"""
	Converts the configuration values for the bot status into a discord.Activity object and a discord.Status object.

	:param configuration_manager: The ConfigurationManager object to use to get the configuration values.
	"""
	
	config = await configuration_manager.get_value("discord_status")

	activity = config["activity"]
	activity_text = config["activity_text"]
	activity_url = config["activity_url"]
	status = config["status"]

	if activity == 0:
		return discord.Game(activity_text), __status_int_to_discord_object(status)
	elif activity == 1:
		return discord.Streaming(name=activity_text, url=activity_url), __status_int_to_discord_object(status)
	elif activity == 2:
		return discord.Activity(type=discord.ActivityType.watching, name=activity_text), __status_int_to_discord_object(status)
	elif activity == 3:
		return discord.Activity(type=discord.ActivityType.listening, name=activity_text), __status_int_to_discord_object(status)
	elif activity == 4:
		return discord.CustomActivity(name=activity_text), __status_int_to_discord_object(status)


def __status_int_to_discord_object(status: int) -> discord.Status:
	"""
	Converts an integer to a discord.Status object. Integers are used within the configuration file to represent
	a status.

	:param status: The integer to convert to a discord.Status object.
	"""

	if status == 0:
		return discord.Status.online
	elif status == 1:
		return discord.Status.idle
	elif status == 2:
		return discord.Status.dnd
	elif status == 3:
		return discord.Status.invisible
