import discord
from discord.ext import commands

from ..GeneralUtilities import PermissionHandler


class AccessControl(commands.Cog):
	"""Limit feature access for users who misbehave."""
	
	access_control = discord.SlashCommandGroup("access_control", description="Limit feature access for users who misbehave.")

	def __init__(self, management_portal_handler):
		self.mph = management_portal_handler

	@discord.option(
		name="user",
		description="The user to toggle command access for.",
		type=discord.User,
		required=True
	)
	@discord.option(
		name="command",
		description="The command to toggle access for.",
		type=str,
		required=True
	)
	@access_control.command()
	@commands.guild_only()
	async def toggle_command_access(self, ctx: discord.ApplicationContext, user: discord.User, command: str):
		"""Toggle access to a specific command. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "access_control", "toggle_command_access", True)
		if not failedPermissionCheck:
			await self.mph.access_control.toggle_command_access(user.id, ctx.guild_id, command)

			embed.title = "Command Access Toggled"
			embed.description = f"Command access for {user.mention} has been toggled for `{command}`."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("access_control", "toggle_command_access", ctx.guild.id)

	@discord.option(
		name="user",
		description="The user to toggle command access for.",
		type=discord.User,
		required=True
	)
	@discord.option(
		name="module",
		description="The module to toggle access for.",
		type=str,
		required=True
	)
	@access_control.command()
	@commands.guild_only()
	async def toggle_module_access(self, ctx: discord.ApplicationContext, user: discord.User, module: str):
		"""Toggle access to a specific module. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "access_control", "toggle_module_access", True)
		if not failedPermissionCheck:
			await self.mph.access_control.toggle_module_access(user.id, ctx.guild_id, module)

			embed.title = "Module Access Toggled"
			embed.description = f"Module access for {user.mention} has been toggled for `{module}`."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("access_control", "toggle_module_access", ctx.guild.id)

	@discord.option(
		name="user",
		description="The user to get banned commands for.",
		type=discord.User,
		required=True
	)
	@access_control.command()
	@commands.guild_only()
	async def list_banned_commands(self, ctx: discord.ApplicationContext, user: discord.User):
		"""List all commands a user is banned from using. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "access_control", "list_banned_commands", True)
		if not failedPermissionCheck:
			banned_commands = await self.mph.access_control.get_banned_commands(user.id, ctx.guild_id)
			if len(banned_commands) == 0:
				embed.title = "No Banned Commands"
				embed.description = f"{user.mention} is not banned from using any commands."
			else:
				embed.title = "Banned Commands"
				embed.description = f"{user.mention} is banned from using the following commands:\n"

				# Split the string by commas, then sort the list alphabetically
				banned_commands = banned_commands.split(",")
				banned_commands.sort()

				# Add each command to the embed description
				for command in banned_commands:
					embed.description += f"- `{command}`\n"

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("access_control", "list_banned_commands", ctx.guild.id)

	@discord.option(
		name="user",
		description="The user to get banned modules for.",
		type=discord.User,
		required=True
	)
	@access_control.command()
	@commands.guild_only()
	async def list_banned_modules(self, ctx: discord.ApplicationContext, user: discord.User):
		"""List all modules a user is banned from using. Only available to administrators."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, self.mph, embed, "access_control", "list_banned_modules", True)
		if not failedPermissionCheck:
			banned_modules = await self.mph.access_control.get_banned_modules(user.id, ctx.guild_id)
			if len(banned_modules) == 0:
				embed.title = "No Banned Modules"
				embed.description = f"{user.mention} is not banned from using any modules."
			else:
				embed.title = "Banned Modules"
				embed.description = f"{user.mention} is banned from using the following modules:\n"

				# Split the string by commas, then sort the list alphabetically
				banned_modules = banned_modules.split(",")
				banned_modules.sort()

				# Add each command to the embed description
				for module in banned_modules:
					embed.description += f"- `{module}`\n"

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("access_control", "list_banned_modules", ctx.guild.id)
