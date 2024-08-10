import discord
from discord.ext import commands, tasks

from Framework.CommandGroups.BasicCog import BasicCog
from Framework.GeneralUtilities import PermissionHandler


class CurseForge(BasicCog):
	"""Automatically announce updates from CurseForge projects."""

	curseforge = discord.SlashCommandGroup("curseforge", description="Automatically announce updates from CurseForge projects.")

	@discord.option(
		name="project_id",
		description="The CurseForge project ID.",
		type=int,
		required=True
	)
	@discord.option(
		name="announcement_channel",
		description="The channel to announce updates in.",
		type=discord.TextChannel,
		required=True
	)
	@curseforge.command()
	@commands.guild_only()
	async def add_project(self, ctx: discord.ApplicationContext, project_id: int, announcement_channel: discord.TextChannel):
		"""Add a new CF project to the update checker."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "curseforge")
		embed, has_key = await self.check_for_api_key(embed)

		if not failed_permission_check and has_key:

			# Set the API key in headers
			headers = {"x-api-key": self.cm.get_value("curseforge/cf_api_key")}

			response = await self.wbh.get(f"https://api.curseforge.com/v1/mods/{project_id}", headers)
			response = response["data"]

			name = response["name"]
			summary = response["summary"]
			logo_url = response["logo"]["url"]
			download_count = response["downloadCount"]
			latest_file_id = response["latestFilesIndexes"][0]["fileId"]

			if await self.sql_bridge.cf_module.add_project(ctx.guild_id, project_id, announcement_channel.id, latest_file_id):
				embed.title = "CurseForge Project Added: " + name
				embed.set_thumbnail(url=logo_url)
				embed.add_field(name="Downloads", value=f"{download_count:,}", inline=True)
				embed.add_field(name="Project ID", value=str(project_id), inline=True)
				embed.description = f"""
				```{summary}```
				The project will now be checked for updates every ten minutes.
				New releases will be posted in {announcement_channel.mention}.
				"""
			else:
				embed.title = "CurseForge Project Already Added"
				embed.description = f"Project `{project_id}` is already being checked for updates."

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("curseforge", "add_project", ctx.guild.id)

	@discord.option(
		name="project_id",
		description="The CurseForge project ID.",
		type=int,
		required=True
	)
	@curseforge.command()
	@commands.guild_only()
	async def remove_project(self, ctx: discord.ApplicationContext, project_id: int):
		"""Remove a CF project from the update checker."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "curseforge")
		embed, has_key = await self.check_for_api_key(embed)

		if not failed_permission_check and has_key:
			await self.sql_bridge.cf_module.remove_project(ctx.guild_id, project_id)

			embed.title = "CurseForge Project Removed"
			embed.description = f"Project `{project_id}` will no longer be checked for updates."

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("curseforge", "remove_project", ctx.guild.id)

	@curseforge.command()
	@commands.guild_only()
	async def list_projects(self, ctx: discord.ApplicationContext):
		"""List all CF projects being checked for updates."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "curseforge")
		embed, has_key = await self.check_for_api_key(embed)

		if not failed_permission_check and has_key:
			projects = await self.sql_bridge.cf_module.get_projects(ctx.guild_id)

			embed.title = "CurseForge Projects"

			if len(projects) == 0:
				embed.description = """
				There are no projects being checked for updates. Use `/curseforge add_project` to add one.
				"""
			else:
				embed.description = "The following projects are being checked for updates:"

				for project in projects:
					# Set the API key in headers
					headers = {"x-api-key": self.cm.get_value("curseforge/cf_api_key")}

					response = await self.wbh.get(f"https://api.curseforge.com/v1/mods/{project[0]}", headers)
					response = response["data"]

					name = response["name"]

					embed.add_field(name=name, value=f"ID: `{project[0]}`\nChannel: {ctx.guild.get_channel(project[1]).mention}", inline=False)

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("curseforge", "list_projects", ctx.guild.id)

	@curseforge.command()
	@commands.guild_only()
	async def check_for_updates(self, ctx: discord.ApplicationContext):
		"""Manually check for updates on CF projects."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "curseforge")
		embed, has_key = await self.check_for_api_key(embed)

		if not failed_permission_check and has_key:
			await self.check_for_updates(ctx.guild_id)

			embed.title = "CurseForge Update Check"
			embed.description = "The update check has been manually run."

		await ctx.respond(embed=embed)
		await self.update_usage_analytics("curseforge", "check_for_updates", ctx.guild.id)

	@tasks.loop(seconds=600)
	async def check_for_updates(self, guild_id: int = None):
		# Get projects list
		if guild_id is None:
			projects = await self.sql_bridge.cf_module.get_projects()
		else:
			projects = await self.sql_bridge.cf_module.get_projects(guild_id)

		# Compare the current file IDs with the latest ones on CF
		for project in projects:
			# Set the API key in headers
			headers = {"x-api-key": self.cm.get_value("curseforge/cf_api_key")}

			response = await self.wbh.get(f"https://api.curseforge.com/v1/mods/{project[0]}", data=headers)
			response = response["data"]

			latest_file_id = response["latestFilesIndexes"][0]["fileId"]

			if project[2] != latest_file_id:
				# Update the latest file ID
				await self.sql_bridge.cf_module.update_project_version(project[0], latest_file_id)

				# Get the announcement channel
				announcement_channel = self.bot.get_channel(project[1])

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
				embed.add_field(name="Project ID", value=project[0], inline=True)
				embed.description = f"""
				```{response["summary"]}```
				"""
				embed.url = f"https://www.curseforge.com/minecraft/mc-mods/{response['slug']}/files/{latest_file_id}"

				# Send the embed
				await announcement_channel.send(embed=embed)

	async def check_for_api_key(self, embed: discord.Embed) -> (discord.Embed, bool):
		"""Check if a CurseForge API key exists, returning an error message in the provided embed if it doesn't."""
		if self.cm.get_value("curseforge/cf_api_key") == "":
			embed.title = "CurseForge API Key Required"
			embed.description = "No CurseForge API key found. Please ask an administrator to set one in the bot configuration."

			return embed, False

		return embed, True
