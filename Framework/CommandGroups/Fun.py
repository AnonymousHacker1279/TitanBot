import discord
from discord.ext import commands

from ..GeneralUtilities import PermissionHandler


class Fun(commands.Cog):
	"""Have fun by messing with other people."""

	@commands.command(name='stab')
	@commands.guild_only()
	async def stab(self, ctx, user=None):
		"""Stab someone, or something."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "fun", "stab")
		if not failedPermissionCheck:
			if user is None:
				embed.title = "Failed to stab"
				embed.description = "You have to tell me who you want to stab."
			else:
				embed.title = "A BLOODY MASSACRE"
				embed.description = "*" + user + " was stabbed by " + ctx.message.author.mention + "*"

		await ctx.send(embed=embed)
