import json
from datetime import date
from random import randint

import requests as requests
from discord.ext import commands
import discord

from ..GeneralUtilities import CommandAccess, Constants


class Utility(commands.Cog):
	"""Get some work done with tools and utilities."""

	@commands.command(name='age')
	@commands.guild_only()
	async def age(self, ctx):
		"""See the length of time I have existed."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("utility"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "utility"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "age"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			birthDate = date(2021, 7, 15)
			todayDate = date.today()
			delta = todayDate - birthDate

			embed.title = "My Age"
			embed.description = "I am **" + str(delta.days) + "** days old."
			embed.set_footer(text="Born into the world on 7/15/21.")

		await ctx.send(embed=embed)

	@commands.command(name='coinFlip')
	@commands.guild_only()
	async def coin_flip(self, ctx):
		"""Flip a coin."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("utility"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "utility"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "coinFlip"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			embed.title = "Coin Flip"
			if randint(0, 1) == 0:
				value = "Heads"
			else:
				value = "Tails"
			embed.description = "Result: **" + value + ".**"

		await ctx.send(embed=embed)

	@commands.command(name='rollDie')
	@commands.guild_only()
	async def roll_die(self, ctx, *sides: int):
		"""Roll a die. Defaults to six sides if not specified."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("utility"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "utility"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "rollDie"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			embed.title = "Roll Die"
			if len(sides) == 0:
				embed.description = "Result: **" + str(randint(1, 6)) + ".**"
			elif sides[0] > 1:
				embed.description = "Result: **" + str(randint(1, sides[0])) + ".**"
			else:
				embed.title = "Roll Die Failed"
				embed.description = "You must specify more than one side on the die."

		await ctx.send(embed=embed)

	@commands.command(name='ping')
	@commands.guild_only()
	async def ping(self, ctx):
		"""Get the latency of the bot."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("utility"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "utility"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "ping"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
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

	@commands.command(name='about')
	@commands.guild_only()
	async def about(self, ctx):
		"""Learn about me."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("utility"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "utility"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "about"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
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
			embed.set_footer(text="AnonymousHacker1279, " + str(date.today().year))

		await ctx.send(embed=embed)
