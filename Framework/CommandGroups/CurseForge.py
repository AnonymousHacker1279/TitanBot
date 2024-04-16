import discord
from discord.ext import commands

from Framework.CommandGroups.BasicCog import BasicCog
from Framework.ConfigurationManager import ConfigurationValues
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
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "curseforge", "add_project")
		if not failed_permission_check:

			# Set the API key in headers
			headers = {"x-api-key": ConfigurationValues.CF_API_TOKEN}

			response = await self.mph.get(f"https://api.curseforge.com/v1/mods/{project_id}", headers, True)
			response = response["data"]

			name = response["name"]
			summary = response["summary"]
			logo_url = response["logo"]["url"]
			download_count = response["downloadCount"]
			latest_file_id = response["latestFilesIndexes"][0]["fileId"]

			await self.mph.cf_checker_api.add_project(ctx.guild_id, project_id, announcement_channel.id, latest_file_id)

			embed.title = "CurseForge Project Added: " + name
			embed.set_thumbnail(url=logo_url)
			embed.add_field(name="Downloads", value=f"{download_count:,}", inline=True)
			embed.add_field(name="Project ID", value=project_id, inline=True)
			embed.description = f"""
			```{summary}```
			The project will now be checked for updates every ten minutes.
			New releases will be posted in {announcement_channel.mention}.
			"""

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("curseforge", "add_project", ctx.guild.id)

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
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "curseforge", "remove_project")
		if not failed_permission_check:
			await self.mph.cf_checker_api.remove_project(ctx.guild_id, project_id)

			embed.title = "CurseForge Project Removed"
			embed.description = f"Project `{project_id}` will no longer be checked for updates."

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("curseforge", "remove_project", ctx.guild.id)

	@curseforge.command()
	@commands.guild_only()
	async def list_projects(self, ctx: discord.ApplicationContext):
		"""List all CF projects being checked for updates."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "curseforge", "list_projects")
		if not failed_permission_check:
			projects = await self.mph.cf_checker_api.get_projects(ctx.guild_id)

			embed.title = "CurseForge Projects"

			if len(projects) == 0:
				embed.description = """
				There are no projects being checked for updates. Use `/add_project` to add one.
				"""
			else:
				embed.description = "The following projects are being checked for updates:"

				for project in projects:
					# Set the API key in headers
					headers = {"x-api-key": ConfigurationValues.CF_API_TOKEN}

					response = await self.mph.get(f"https://api.curseforge.com/v1/mods/{project['project_id']}", headers, True)
					response = response["data"]

					name = response["name"]

					embed.add_field(name=name, value=f"ID: `{project['project_id']}`\nChannel: {ctx.guild.get_channel(project['announcement_channel_id']).mention}", inline=False)

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("curseforge", "list_projects", ctx.guild.id)

	@curseforge.command()
	@commands.guild_only()
	async def check_for_updates(self, ctx: discord.ApplicationContext):
		"""Manually check for updates on CF projects."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failed_permission_check = await PermissionHandler.check_permissions(ctx, embed, "curseforge", "check_for_updates")
		if not failed_permission_check:
			await self.mph.cf_checker_api.check_for_updates(ctx.guild_id)

			embed.title = "CurseForge Update Check"
			embed.description = "The update check has been manually run."

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("curseforge", "check_for_updates", ctx.guild.id)
