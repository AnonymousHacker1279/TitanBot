import sys
from datetime import date
from random import randint

import discord
import psutil as psutil
from discord import HTTPException
from discord.ext import commands

from Framework.ConfigurationManager import ConfigurationValues
from .BasicCog import BasicCog
from ..GeneralUtilities import PermissionHandler


class Utility(BasicCog):
	"""Get some work done with tools and utilities."""

	utility = discord.SlashCommandGroup("utility", description="Get some work done with tools and utilities.")

	@utility.command()
	@commands.guild_only()
	async def age(self, ctx: discord.ApplicationContext):
		"""See the length of time I have existed."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "age")
		if not failedPermissionCheck:
			birthDate = date(2021, 7, 15)
			todayDate = date.today()
			delta = todayDate - birthDate

			embed.title = "My Age"
			embed.description = "I am **" + str(delta.days) + "** days old."
			embed.set_footer(text="Born into the world on 7/15/21.")

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("utility", "age", ctx.guild.id)

	@utility.command()
	@commands.guild_only()
	async def coin_flip(self, ctx: discord.ApplicationContext):
		"""Flip a coin."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "coin_flip")
		if not failedPermissionCheck:
			embed.title = "Coin Flip"
			if randint(0, 1) == 0:
				value = "Heads"
			else:
				value = "Tails"
			embed.description = "Result: **" + value + ".**"

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("utility", "coin_flip", ctx.guild.id)

	@discord.option(
		name="sides",
		description="The number of sides on the die.",
		type=int,
		required=False
	)
	@utility.command()
	@commands.guild_only()
	async def roll_die(self, ctx: discord.ApplicationContext, sides: int = 6):
		"""Roll a die. Defaults to six sides if not specified."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "roll_die")
		if not failedPermissionCheck:
			embed.title = "Roll Die"
			if sides > 0:
				embed.description = "Result: **" + str(randint(1, sides)) + ".**"
			else:
				embed.title = "Roll Die Failed"
				embed.description = "You must specify more than one side on the die."

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("utility", "roll_die", ctx.guild.id)

	@utility.command()
	@commands.guild_only()
	async def ping(self, ctx: discord.ApplicationContext):
		"""Get the latency of the bot."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "ping")
		if not failedPermissionCheck:
			embed.title = "Bot Latency"
			latency = round(ctx.bot.latency * 1000)
			embed.description = "Current Bot Latency: **" + str(latency) + " ms**\n"
			if 175 < latency < 250:
				embed.description += "Latency is moderate. Expect potential delays and drops."
			elif 251 < latency < 325:
				embed.description += "Latency is high. Delays and dropped messages are likely."
			elif latency > 326:
				embed.description += "Latency is extremely high. Delays and drops are nearly assured."

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("utility", "ping", ctx.guild.id)

	@utility.command()
	@commands.guild_only()
	async def about(self, ctx: discord.ApplicationContext):
		"""Learn about me."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "about")
		if not failedPermissionCheck:
			embed.title = "About Me"
			embed.description = "I'm **TitanBot**, an intelligent software built by **AnonymousHacker1279.**\n"
			embed.description += "Providing features to servers since 7/15/21.\n\n"

			# Get the latest version from GitHub
			response = await self.mph.get(f"https://api.github.com/repos/{ConfigurationValues.UPDATE_REPOSITORY}/releases/latest", non_management_portal=True)
			latest_version = response["tag_name"]
			changelog = response["body"]

			embed.description += f"Current Version: **{ConfigurationValues.VERSION}**\nLatest Published Version: **{latest_version}**\n"
			embed.description += f"What's new, in the latest version: \n```txt\n{changelog}\n```\n"
			embed.description += "See the wiki for more information and help. https://github.com/AnonymousHacker1279/TitanBot/wiki"
			embed.set_footer(text="AnonymousHacker1279, " + str(date.today().year))

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("utility", "about", ctx.guild.id)

	@utility.command()
	@commands.guild_only()
	async def total_users(self, ctx: discord.ApplicationContext):
		"""Get the total number of users in the server."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "total_users")
		if not failedPermissionCheck:
			embed.title = "Total Users"
			embed.description = "There are **" + str(ctx.guild.member_count) + "** users here."

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("utility", "total_users", ctx.guild.id)

	@utility.command()
	@commands.guild_only()
	async def status(self, ctx: discord.ApplicationContext):
		"""Get the current system status."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "status")
		if not failedPermissionCheck:
			embed.title = "System Status"

			cpu_usage = psutil.cpu_percent(interval=0.1)
			cpu_count = psutil.cpu_count()
			system_memory_usage = psutil.virtual_memory()[2]
			total_system_memory = round(psutil.virtual_memory()[0] / (1024 * 1024 * 1024), 2)

			embed.description = "CPU Information: **" \
								+ str(cpu_usage) + "% usage, " \
								+ str(cpu_count) + " cores**\n"
			embed.description += "Memory Information: **"\
								+ str(system_memory_usage) + "% usage, "\
								+ str(total_system_memory) + "GB total**\n"
			embed.description += "Disk Information: **" \
								+ str(psutil.disk_usage('/')[3]) + "% usage, " \
								+ str(round(psutil.disk_usage('/')[0] / (1024 * 1024 * 1024), 2)) + "GB total**\n"

			embed.description += "\nDiscord Metrics: **" \
								+ str(len(ctx.bot.guilds)) + " servers, " \
								+ str(len(ctx.bot.users)) + " users**\n"

			embed.description += "\nBot Setup: **" \
								+ "TitanBot " + ConfigurationValues.VERSION + "\n" \
								+ "- Python " + str(sys.version_info[0]) + "." + str(sys.version_info[1]) + "." + str(sys.version_info[2]) + "\n" \
								+ "- Pycord " + str(discord.__version__) + "**\n"

			if cpu_usage > 70:
				embed.description += ":warning: High CPU usage, responsiveness may be degraded.\n"
			if system_memory_usage > 80:
				embed.description += ":warning: High memory usage, responsiveness may be degraded.\n"

		await ctx.respond(embed=embed)
		await self.update_management_portal_command_used("utility", "status", ctx.guild.id)

	@discord.option(
		name="url",
		description="The URL to generate a QR code for.",
		type=str,
		required=True
	)
	@discord.option(
		name="transparent",
		description="Whether or not the QR code should be transparent.",
		type=bool,
		required=False
	)
	@discord.option(
		name="pixel_size",
		description="The size of each pixel in the QR code.",
		type=int,
		required=False
	)
	@utility.command()
	@commands.guild_only()
	async def qr_generator(self, ctx: discord.ApplicationContext, url: str, transparent: bool = False, pixel_size: int = 5):
		"""Generate a QR code containing a URL."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "qr_generator")
		if not failedPermissionCheck:
			# Build the API URL
			api_url = "https://qrtag.net/api/qr"
			if transparent:
				api_url += "_transparent"
			api_url += "_" + str(pixel_size) + ".png?url=" + url

			# Get the QR code
			embed.title = "Generated QR Code"
			embed.set_image(url=api_url)

		try:
			await ctx.respond(embed=embed)
		except HTTPException:
			# Reset the embed
			embed = discord.Embed(color=discord.Color.dark_blue(),
								title="Failed to generate QR code",
								description='The QR code could not be generated. Check the URL and try again.')

			await ctx.respond(embed=embed)

		await self.update_management_portal_command_used("utility", "qr_generator", ctx.guild.id)
