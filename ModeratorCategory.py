from discord.ext import commands
from discord import utils
import json

class Moderators(commands.Cog):
	"""Need help from a moderator? Take a look here."""

	@commands.command(name='moderators')
	@commands.guild_only()
	async def moderators(self, ctx):
		"""How to request moderators"""
		response = "You can request help from a moderator by pinging @Micro Titan.\n"
		response += "Pinging unnecessarily or without reason is a punishable offense."
		await ctx.send(response)

	@commands.command(name='ban')
	@commands.guild_only()
	async def ban(self, ctx):
		"""Get the out (totally a real command)."""
		response = "https://etithespir.it/random/remove.mp4"
		await ctx.send(response)

	@commands.command(name='noquote')
	@commands.guild_only()
	async def noquote(self, ctx, givenUser=""):
		"""Revoke a user's addquote privileges."""

		if givenUser != "":
			role = utils.get(ctx.guild.roles, id=865619566334574603)
			if role in ctx.message.author.roles:
				with open('noquote_users.json', 'r') as f:
					data = json.load(f)
					modifiedData = list(data)
					maxIndex = 0
					userIndex = None
					flag = False
					for i in data:
						maxIndex = maxIndex + 1
						if givenUser in i['user']:
							userIndex = maxIndex
					if userIndex != None:
						modifiedData.remove(data[userIndex - 1])
						flag = True
					else:
						userDictionary = {"user": givenUser}
						modifiedData.append(userDictionary)
						flag = False

				with open('noquote_users.json', 'w') as f:
					json.dump(modifiedData, f, indent=4)
					if flag == True:
						response = "Addquote privileges restored to user."
					else:
						response = "Addquote privileges revoked from user."
			else:
				response = "You don't have the proper permissions for this action. Come back when you're more important."
		else:
			response = "You need to specify a user, dummy."
		await ctx.send(response)