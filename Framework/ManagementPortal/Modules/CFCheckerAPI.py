import discord
from discord.ext import tasks

from Framework.ConfigurationManager import ConfigurationValues
from Framework.ManagementPortal.APIEndpoints import APIEndpoints
from Framework.ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


class CFCheckerAPI:

	def __init__(self, management_portal_handler: ManagementPortalHandler):
		self.mph = management_portal_handler

	@tasks.loop(seconds=600)
	async def check_for_updates(self, guild_id: int = None):
		# Get projects list
		if guild_id is None:
			projects = await self.get_projects()
		else:
			projects = await self.get_projects(guild_id)

		# Compare the current file IDs with the latest ones on CF
		for project in projects:
			# Set the API key in headers
			headers = {"x-api-key": ConfigurationValues.CF_API_TOKEN}

			response = await self.mph.get(f"https://api.curseforge.com/v1/mods/{project['project_id']}", data=headers, non_management_portal=True)
			response = response["data"]

			latest_file_id = response["latestFilesIndexes"][0]["fileId"]

			if project["latest_file_id"] != latest_file_id:
				# Update the latest file ID
				await self.update_project(project["guild_id"], project["project_id"], latest_file_id)

				# Get the announcement channel
				announcement_channel = self.mph.bot.get_channel(project["announcement_channel_id"])

				# Get the release type
				release_type = response["latestFilesIndexes"][0]["releaseType"]
				if release_type == 1:
					release_type = "Release"
				elif release_type == 2:
					release_type = "Beta"
				elif release_type == 3:
					release_type = "Alpha"

				# Create the embed
				embed = discord.Embed(color=discord.Color.dark_blue(), description='')
				embed.title = "New Release: " + response["name"]
				embed.set_thumbnail(url=response["logo"]["url"])
				embed.add_field(name="Release Type", value=release_type, inline=True)
				embed.add_field(name="File Name", value=response["latestFilesIndexes"][0]["filename"], inline=True)
				embed.add_field(name="Downloads", value=f"{response['downloadCount']:,}", inline=True)
				embed.add_field(name="Project ID", value=project["project_id"], inline=True)
				embed.description = f"""
				```{response["summary"]}```
				"""
				embed.url = f"https://www.curseforge.com/minecraft/mc-mods/{response['slug']}/files/{latest_file_id}"

				# Send the embed
				await announcement_channel.send(embed=embed)

	async def add_project(self, guild_id: int, project_id: int, announcement_channel_id: int, latest_file_id: int):
		headers = self.mph.base_data.copy()
		headers["type"] = "add"
		headers["guild_id"] = str(guild_id)
		headers["project_id"] = str(project_id)
		headers["announcement_channel_id"] = str(announcement_channel_id)
		headers["latest_file_id"] = str(latest_file_id)

		return await self.mph.post(APIEndpoints.MODIFY_CF_UPDATE_CHECKER, headers)

	async def remove_project(self, guild_id: int, project_id: int):
		headers = self.mph.base_data.copy()
		headers["type"] = "remove"
		headers["guild_id"] = str(guild_id)
		headers["project_id"] = str(project_id)
		headers["announcement_channel_id"] = ""
		headers["latest_file_id"] = ""

		return await self.mph.post(APIEndpoints.MODIFY_CF_UPDATE_CHECKER, headers)

	async def get_projects(self, guild_id: int = None):
		headers = self.mph.base_data.copy()

		if guild_id is not None:
			headers["guild_id"] = str(guild_id)

		return await self.mph.get(APIEndpoints.GET_CF_PROJECTS, headers)

	async def update_project(self, guild_id: int, project_id: int, latest_file_id: int):
		headers = self.mph.base_data.copy()
		headers["guild_id"] = str(guild_id)
		headers["project_id"] = str(project_id)
		headers["latest_file_id"] = str(latest_file_id)

		return await self.mph.post(APIEndpoints.UPDATE_CF_PROJECT, headers)
