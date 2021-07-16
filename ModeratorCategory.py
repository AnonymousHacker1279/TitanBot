from discord.ext import commands

class Moderators(commands.Cog):
	"""Need help from a moderator? Take a look here."""

	@commands.command(name='moderators')
	@commands.guild_only()
	async def moderators(self, ctx):
		"""How to request moderators"""
		response = "You can request help from a moderator by pinging @Micro Titan.\n"
		response = response + "Pinging unnecessarily or without reason is a punishable offense."
		await ctx.send(response)
