import discord
from discord.ext import commands

from ..Osmium import Osmium
from ..GeneralUtilities import PermissionHandler
from ..GeneralUtilities import GeneralUtilities as Utilities


class CustomCommands(commands.Cog):
	"""Expand the power of TitanBot with custom commands."""

	@commands.command(name='addCommand', aliases=["ac"])
	@commands.guild_only()
	async def add_command(self, ctx, command_name: str = None, code: str = None):
		"""Add a custom command to the archive."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands", "addCommand")
		if not failedPermissionCheck:
			if command_name is not None:
				if code is not None:
					with open(Utilities.get_custom_commands_directory() + command_name + ".js", 'w') as f:
						f.write(code)
					embed.title = "Custom Command Added: " + command_name
					embed.description = "You can now run the custom command by typing $" + command_name
				else:
					embed.title = "Failed to Add Custom Command"
					embed.description = "You must provide code to run with the command."
			else:
				embed.title = "Failed to Add Custom Command"
				embed.description = "You must specify a command name."

		await ctx.send(embed=embed)

	@commands.command(name='runJS', aliases=["rj"])
	@commands.guild_only()
	async def run_javascript(self, ctx, js_c):
		"""Directly execute a block of JavaScript. Useful for testing new commands."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "customCommands",
																				"addCommand", shouldCheckForWizard=True)
		if not failedPermissionCheck:
			osmium = Osmium.Osmium(js_c, "Framework/Osmium/data/lists/import_whitelist.txt")
			if osmium.error is not None:
				embed.title = "Failed to Execute Custom Command"
				embed.description = "An error occurred while executing the custom command.\n```" + osmium.error + "\n```"
			elif osmium.result is not None:
				# Check for colors first, because the embed has to be recreated to change it
				if osmium.result["color"] != "":
					embed = discord.Embed(color=int(osmium.result["color"]), description='')

				embed.title = osmium.result["title"]
				embed.description = osmium.result["description"]
				if osmium.result["image_url"] != "":
					embed.set_image(url=osmium.result["image_url"])
				if osmium.result["footer"] != "":
					embed.set_footer(text=osmium.result["footer"])
				if osmium.result["thumbnail_url"] != "":
					embed.set_thumbnail(url=osmium.result["thumbnail_url"])
				if osmium.result["author"]["name"] != "":
					embed.set_author(name=osmium.result["author"]["name"],
									url=osmium.result["author"]["url"],
									icon_url=osmium.result["author"]["image_url"])
				if osmium.result["fields"]["entries"]["count"] != 0:
					for entry in osmium.result["fields"]["entries"]:
						embed.add_field(name=entry,
										value=osmium.result["fields"]["entries"][entry]["value"],
										inline=osmium.result["fields"]["entries"][entry]["inline"])

		await ctx.send(embed=embed)
