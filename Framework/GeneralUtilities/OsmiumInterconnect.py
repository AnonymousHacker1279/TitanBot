import discord

from Framework.Osmium.Osmium import Osmium


async def execute_with_osmium(management_portal_handler, guild_id: int, js_code, arguments: list, embed: discord.Embed):
	osmium = Osmium(management_portal_handler, guild_id, js_code, arguments, "Framework/Osmium/data/lists/import_whitelist.txt")
	if osmium.error is not None:
		embed.title = "Failed to Execute Custom Command"
		embed.description = "An error occurred while executing the custom command.\n```" + osmium.error + "\n```"
	elif osmium.result is not None:
		# Check for colors first, because the embed has to be recreated to change it
		if osmium.result["color"] != "":
			embed = discord.Embed(color=int(osmium.result["color"]), description='')

		embed.title = str(osmium.result["title"])
		embed.description = str(osmium.result["description"])
		if osmium.result["image_url"] != "":
			embed.set_image(url=str(osmium.result["image_url"]))
		if osmium.result["footer"] != "":
			embed.set_footer(text=str(osmium.result["footer"]))
		if osmium.result["thumbnail_url"] != "":
			embed.set_thumbnail(url=str(osmium.result["thumbnail_url"]))
		if osmium.result["author"]["name"] != "":
			embed.set_author(name=str(osmium.result["author"]["name"]),
							url=str(osmium.result["author"]["url"]),
							icon_url=str(osmium.result["author"]["image_url"]))
		if osmium.result["fields"]["count"] != 0:
			for entry in osmium.result["fields"]["entries"]:
				embed.add_field(name=entry,
							value=str(osmium.result["fields"]["entries"][entry]["value"]),
							inline=bool(osmium.result["fields"]["entries"][entry]["inline"]))

	# Do some checking on required embed elements
	if embed.title == "":
		embed.title = "Null"
	if embed.description == "":
		embed.description = "Null"

	return embed
