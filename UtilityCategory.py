from random import randint
import discord
from discord.ext import commands
from datetime import date

class Utility(commands.Cog):
	"""Get some work done with a utility function."""

	@commands.command(name='totalusers')
	@commands.guild_only()
	async def totalusers(self, ctx):
		"""Get the total number of users in the server (excluding bots)."""
		role = discord.utils.get(ctx.guild.roles, id=750071002062520411)
		bot_count = len(role.members)
		response = "Total users: **" + str(ctx.guild.member_count - bot_count) + "**"
		await ctx.send(response)

	@commands.command(name='ping')
	async def ping(self, ctx):
		"""Get the latency of the bot."""
		response = "Current Bot Latency: **" + str(round(ctx.bot.latency * 1000)) + " ms**"
		await ctx.send(response)

	@commands.command(name='about')
	async def about(self, ctx):
		"""Learn about me."""
		response = "I'm an extremely intelligent software designed to make your lives harder.\n"
		response += "Providing useless features to Titan Programming since 7/15/21.\n\n"
		response += "See $help for command information."
		await ctx.send(response)

	@commands.command(name='age')
	async def age(self, ctx):
		"""See how old I am."""
		d0 = date(2021, 7, 15)
		d1 = date.today()
		delta = d1 - d0

		response = "I am **" + str(delta.days) + "** days old." 
		await ctx.send(response)

	@commands.command(name='today')
	async def today(self, ctx):
		"""Get the current day. I should hope you don't have to ask a Discord bot that question."""
		response = "Today is **" + str(date.today()) + "**." 
		await ctx.send(response)

	@commands.command(name='website')
	async def website(self, ctx):
		"""Get our website URL."""
		response = "Our website can be located at https://titan-mk4.dynv6.net." 
		await ctx.send(response)

	@commands.command(name='flipcoin')
	async def flipcoin(self, ctx):
		"""Flip a coin."""
		if randint(0,1) == 0:
			value = "Heads"
		else:
			value = "Tails"
		response = "Result: **" + value + ".**"
		await ctx.send(response)

	@commands.command(name='rolldice')
	async def rolldice(self, ctx, *sides:int):
		"""Roll a 6 sided die. Alternatively, pass in the number of sides."""
		if str(sides) == "()":
			response = "Result: **" + str(randint(1,6)) + ".**"
		elif sides[0] > 1:
			response = "Result: **" + str(randint(1,sides[0])) + ".**"
		else:
			response = "You need to give me a number greater than 1, dingus."
		await ctx.send(response)