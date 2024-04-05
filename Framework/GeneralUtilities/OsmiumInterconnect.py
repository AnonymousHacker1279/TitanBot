import discord

# from Framework.Osmium.Osmium import Osmium


async def execute_with_osmium(osmium, js_code, arguments: list, max_execution_time: int, embed: discord.Embed):
	# TODO: re-implement once js2py is up to date, or look for alternatives
	# result, error = await osmium.execute(js_code, arguments, max_execution_time)
	error = "Custom Commands are currently unavailable due to js2py not supporting Python 3.12"
	result = []
	if error is not None:
		embed.title = "Failed to Execute Custom Command"
		embed.description = "An error occurred while executing the custom command.\n```" + error + "\n```"
	elif result is not None:
		# Check for colors first, because the embed has to be recreated to change it
		if result["color"] != "":
			embed = discord.Embed(color=int(result["color"]), description='')

		embed.title = str(result["title"])
		embed.description = str(result["description"])
		if result["image_url"] != "":
			embed.set_image(url=str(result["image_url"]))
		if result["footer"] != "":
			embed.set_footer(text=str(result["footer"]))
		if result["thumbnail_url"] != "":
			embed.set_thumbnail(url=str(result["thumbnail_url"]))
		if result["author"]["name"] != "":
			embed.set_author(name=str(result["author"]["name"]),
							url=str(result["author"]["url"]),
							icon_url=str(result["author"]["image_url"]))
		if result["fields"]["count"] != 0:
			for entry in result["fields"]["entries"]:
				embed.add_field(name=entry,
							value=str(result["fields"]["entries"][entry]["value"]),
							inline=bool(result["fields"]["entries"][entry]["inline"]))

	# Do some checking on required embed elements
	if embed.title == "":
		embed.title = "Null"
	if embed.description == "":
		embed.description = "Null"

	return embed
