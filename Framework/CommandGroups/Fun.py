from discord.ext import commands
import discord
from ..GeneralUtilities import CommandAccess


class Fun(commands.Cog):
	"""Have fun by messing with other people."""

	@commands.command(name='stab')
	@commands.guild_only()
	async def stab(self, ctx, user=None):
		"""Stab someone, or something."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		if not await CommandAccess.check_module_enabled("fun"):
			embed.title = "Cannot use this module"
			embed.description = "This module has been disabled."
		elif await CommandAccess.check_user_is_banned_from_module(ctx.message.author.mention, "fun"):
			embed.title = "Cannot use this module"
			embed.description = "You do not have access to use this module."
		elif await CommandAccess.check_user_is_banned_from_command(ctx.message.author.mention, "stab"):
			embed.title = "Cannot use this command"
			embed.description = "You do not have permission to use this command."
		else:
			if user is None:
				embed.title = "Failed to stab"
				embed.description = "You have to tell me who you want to stab."
			else:
				embed.title = "A BLOODY MASSACRE"
				embed.description = "*" + user + " was stabbed by " + ctx.message.author.mention + "*"

		await ctx.send(embed=embed)
