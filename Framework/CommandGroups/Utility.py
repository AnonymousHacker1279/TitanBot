import json
from datetime import date
from random import randint

import discord
import psutil as psutil
import requests as requests
from discord.ext import commands

from ..GeneralUtilities import Constants, PermissionHandler


class Utility(commands.Cog):
	"""Get some work done with tools and utilities."""

	@commands.command(name='age', aliases=["a"])
	@commands.guild_only()
	async def age(self, ctx):
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

		await ctx.send(embed=embed)

	@commands.command(name='coinFlip', aliases=["cf"])
	@commands.guild_only()
	async def coin_flip(self, ctx):
		"""Flip a coin."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "coinFlip")
		if not failedPermissionCheck:
			embed.title = "Coin Flip"
			if randint(0, 1) == 0:
				value = "Heads"
			else:
				value = "Tails"
			embed.description = "Result: **" + value + ".**"

		await ctx.send(embed=embed)

	@commands.command(name='rollDie', aliases=["rd"])
	@commands.guild_only()
	async def roll_die(self, ctx, *sides: int):
		"""Roll a die. Defaults to six sides if not specified."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "rollDie")
		if not failedPermissionCheck:
			embed.title = "Roll Die"
			if len(sides) == 0:
				embed.description = "Result: **" + str(randint(1, 6)) + ".**"
			elif sides[0] > 1:
				embed.description = "Result: **" + str(randint(1, sides[0])) + ".**"
			else:
				embed.title = "Roll Die Failed"
				embed.description = "You must specify more than one side on the die."

		await ctx.send(embed=embed)

	@commands.command(name='ping', aliases=["p"])
	@commands.guild_only()
	async def ping(self, ctx):
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

		await ctx.send(embed=embed)

	@commands.command(name='about', aliases=["ab"])
	@commands.guild_only()
	async def about(self, ctx):
		"""Learn about me."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "about")
		if not failedPermissionCheck:
			embed.title = "About Me"
			embed.description = "I'm **TitanBot**, an intelligent software built by **AnonymousHacker1279.**\n"
			embed.description += "Providing features to servers since 7/15/21.\n\n"
			# Get version information
			updateData = json.loads(requests.get(Constants.UPDATE_LOCATION).text)
			versionTag = updateData[updateData["latest"]]["versionTag"]
			if versionTag == "alpha":
				versionEmoji = ":bug:"
			elif versionTag == "beta":
				versionEmoji = ":bug::hammer:"
			elif versionTag == "release":
				versionEmoji = ":package:"
			elif versionTag == "indev":
				versionEmoji = ":tools:"
			else:
				versionEmoji = ":question:"
			embed.description += "Current Version: **" + Constants.VERSION + "**\n" \
								"Latest Version: (" + versionEmoji + ", " + versionTag + ") **" + updateData["latest"] + "**\n"
			changelog = updateData[updateData["latest"]]["changelog"]
			embed.description += "What's new, in the latest version: \n```txt\n" + \
								changelog + "```\n"
			embed.description += "See the wiki for more information and help. https://github.com/AnonymousHacker1279/TitanBot/wiki"
			embed.set_footer(text="AnonymousHacker1279, " + str(date.today().year))

		await ctx.send(embed=embed)

	@commands.command(name='totalUsers', aliases=["tu"])
	@commands.guild_only()
	async def total_users(self, ctx):
		"""Get the total number of users in the server."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "totalUsers")
		if not failedPermissionCheck:
			embed.title = "Total Users"
			embed.description = "There are **" + str(ctx.guild.member_count) + "** users here."

		await ctx.send(embed=embed)

	@commands.command(name='status', aliases=["sts"])
	@commands.guild_only()
	async def status(self, ctx):
		"""Get the current system status."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "utility", "status")
		if not failedPermissionCheck:
			embed.title = "System Status"

			cpuUsage = psutil.cpu_percent(interval=1)
			cpuCount = psutil.cpu_count()
			systemMemoryUsage = psutil.virtual_memory()[2]
			totalSystemMemory = round(psutil.virtual_memory()[0] / (1024 * 1024 * 1024), 2)

			embed.description = "CPU Information: **" \
								+ str(cpuUsage) + "% usage, " \
								+ str(cpuCount) + " cores**\n"
			embed.description += "Memory Information: **"\
								+ str(systemMemoryUsage) + "% usage, "\
								+ str(totalSystemMemory) + " total GB**\n"

			if cpuUsage > 70:
				embed.description += ":warning: High CPU usage, responsiveness may be degraded.\n"
			if systemMemoryUsage > 80:
				embed.description += ":warning: High memory usage, responsiveness may be degraded.\n"

		await ctx.send(embed=embed)
