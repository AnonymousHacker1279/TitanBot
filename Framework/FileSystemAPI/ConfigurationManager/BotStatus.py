import discord


async def get_status(activity: int, activity_text: str, activity_url: str, status: int):
	if activity == 0:
		return [discord.Game(activity_text), __status_int_to_discord_object(status)]
	elif activity == 1:
		return [discord.Streaming(name=activity_text, url=activity_url), __status_int_to_discord_object(status)]
	elif activity == 2:
		return [discord.Activity(type=discord.ActivityType.watching, name=activity_text), __status_int_to_discord_object(status)]
	elif activity == 3:
		return [discord.Activity(type=discord.ActivityType.listening, name=activity_text), __status_int_to_discord_object(status)]


def __status_int_to_discord_object(status: int):
	if status == 0:
		return discord.Status.online
	elif status == 1:
		return discord.Status.idle
	elif status == 2:
		return discord.Status.dnd
	elif status == 3:
		return discord.Status.invisible
