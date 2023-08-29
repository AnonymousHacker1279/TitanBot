import discord


async def get_status(activity: int, activity_text: str, activity_url: str, activity_emoji: str, status: int) -> list:
	"""
	Converts the configuration values for the bot status into a discord.Activity object and a discord.Status object.

	:param activity: The integer representing the activity type. Used for the Playing/Streaming/Watching/Listening/Custom status.
	:param activity_text: The text to display for the activity.
	:param activity_url: The URL to use for the activity. Only used for streaming.
	:param activity_emoji: The emoji to use for the activity. Only used for custom statuses.
	:param status: The integer representing the status. Used for the Online/Idle/DND/Invisible status.
	"""
	if activity == 0:
		return [discord.Game(activity_text), __status_int_to_discord_object(status)]
	elif activity == 1:
		return [discord.Streaming(name=activity_text, url=activity_url), __status_int_to_discord_object(status)]
	elif activity == 2:
		return [discord.Activity(type=discord.ActivityType.watching, name=activity_text), __status_int_to_discord_object(status)]
	elif activity == 3:
		return [discord.Activity(type=discord.ActivityType.listening, name=activity_text), __status_int_to_discord_object(status)]
	elif activity == 4:
		if activity_emoji != "":
			# Despite CustomActivity having a dedicated emoji field, it doesn't seem to work
			text = activity_emoji + " " + activity_text
			return [discord.CustomActivity(name=text),
					__status_int_to_discord_object(status)]
		else:
			return [discord.CustomActivity(name=activity_text), __status_int_to_discord_object(status)]


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
