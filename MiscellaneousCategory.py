from discord.ext import commands
from random import randint
import discord
import json
import asyncio

class Miscellaneous(commands.Cog):
	"""Miscellaneous commands that exist for no particular reason."""

	@commands.command(name='stab')
	async def stab(self, ctx, *stabbable: str):
		"""Stab someone, or something."""
		if str(stabbable) == "()":
			response = "Well, are you going to stab someone or not?"
		elif "(''," in str(stabbable).translate({ord(i): None for i in '*'}):
			response = "Try again when you can coherently form a word."
		elif "<@!865380885649031178>" in str('{}'.format(' '.join(stabbable).replace('*', ''))):
			response = "*" + str(ctx.message.author.mention) + " was shot by " + str(ctx.bot.user.mention) + "*"
		elif "<@!417794810284474378>" in str('{}'.format(' '.join(stabbable).replace('*', ''))) or "<@!509490815236833280>" in str('{}'.format(' '.join(stabbable).replace('*', ''))) or "<@!567446167827513350>" in str('{}'.format(' '.join(stabbable).replace('*', ''))):
			response = "*" + str(ctx.bot.user.mention) + " intervened and shot " + str('{}'.format(' '.join(stabbable).replace('*', ''))) + "*"
		else:
			response = "*" + str('{}'.format(' '.join(stabbable).replace('*', ''))) + " was stabbed by " + str(ctx.message.author.mention) + "*".lstrip(" ")
		await ctx.send(response)

	@commands.command(name='rock')
	async def rock(self, ctx, *rockable: str):
		"""Throw a rock at someone, or something."""
		if str(rockable) == "()":
			response = "Well, are you going to crush someone or not?"
		elif "(''," in str(rockable).translate({ord(i): None for i in '*'}):
			response = "Try again when you can coherently form a word."
		elif "<@!865380885649031178>" in str('{}'.format(' '.join(rockable).replace('*', ''))):
			response = "*" + str(ctx.message.author.mention) + " was shot by " + str(ctx.bot.user.mention) + "*"
		elif "<@!417794810284474378>" in str('{}'.format(' '.join(rockable).replace('*', ''))) or "<@!509490815236833280>" in str('{}'.format(' '.join(rockable).replace('*', ''))) or "<@!567446167827513350>" in str('{}'.format(' '.join(rockable).replace('*', ''))):
			response = "*" + str(ctx.bot.user.mention) + " intervened and shot " + str('{}'.format(' '.join(rockable).replace('*', ''))) + "*"
		else:
			response = "*" + str('{}'.format(' '.join(rockable).replace('*', ''))) + " was crushed with rocks by " + str(ctx.message.author.mention) + "*".lstrip(" ")
		await ctx.send(response)

	@commands.command(name='quote')
	async def quote(self, ctx, *ID: int):
		"""Get a quote by number. Or a random one if you don't provide that."""
		if str(ID) == "()":
			with open('quote_list.json', 'r') as f:
				data = json.load(f)
				maxIndex = 0
				for i in data:
					maxIndex = maxIndex + 1
				random = randint(1, maxIndex - 1)
				response = "> " + data[random]["content"] + " - " + data[random]["author"] + ". **Quote #" + str(random + 1) + "**"
		elif ID[0] > 0:
			with open('quote_list.json', 'r') as f:
				data = json.load(f)
				maxIndex = 0
				for i in data:
					maxIndex = maxIndex + 1
				if ID[0] - 1 < maxIndex:
					response = "> " + data[ID[0] - 1]["content"] + " - " + data[ID[0] - 1]["author"] + ". **Quote #" + str(ID[0]) + "**"
				else:
					response = "You've given me a quote number higher than the number of quotes I have. My archives contain " + str(ID[0] - 1) + " quotes."
		else:
			response = "You can't have a quote number lower than one, you brainlet."		
		await ctx.send(response)

	@commands.command(name='addquote')
	@commands.guild_only()
	async def addquote(self, ctx, author: str, *quote: str):
		"""Someone said something stupid? Make them remember it by quoting them."""

		with open('quote_list.json', 'r') as f:
			data = json.load(f)
		
		with open('quote_list.json', 'w') as f:
			quoteDictionary = {"content": str('{}'.format(' '.join(quote))) , "author": str(author)}
			data = list(data)
			data.append(quoteDictionary)
			json.dump(data, f, indent=4)
		
		response = "Added quote to archive."
		
		await ctx.send(response)

	@commands.command(name='removequote')
	@commands.guild_only()
	async def removequote(self, ctx, ID: int):
		"""Remove a quote from the archive."""

		if ID > 0:
			role = discord.utils.get(ctx.guild.roles, id=865619566334574603)
			if role in ctx.message.author.roles:
				with open('quote_list.json', 'r') as f:
					data = json.load(f)
					modifiedData = list(data)
					maxIndex = 0
					flag = False
					for i in data:
						maxIndex = maxIndex + 1
					if ID - 1 < maxIndex:
						modifiedData.remove(data[ID - 1])
						flag = True
					else:
						response = "You've given me a quote number higher than the number of quotes I have. My archives contain " + str(maxIndex) + " quotes."
						flag = False

				if flag == True:
					with open('quote_list.json', 'w') as f:
						json.dump(modifiedData, f, indent=4)
						response = "Removed quote from archive."
			else:
				response = "You don't have the proper permissions for this action. Come back when you're more important."
		else:
			response = "You can't remove a quote number lower than one, you brainlet."
		await ctx.send(response)

	@commands.command(name='bruh')
	async def bruh(self, ctx):
		"""Bruh moment."""
		response = "https://cdn.discordapp.com/attachments/694603367531544617/865641424665837618/Bruh_Sound_Effect_2.mp3"
		await ctx.send(response)

	@commands.command(name='oldspice')
	async def oldspice(self, ctx, *speed):
		"""Smell refreshed. Speed can be 'slow' or 'fast'. Must be in a voice channel."""

		if str(ctx.bot.voice_clients) == "[]":
			if ctx.author.voice == None:
				response = "You must be in a voice channel to use this command."
				await ctx.send(response)
			else:
				channel = ctx.author.voice.channel
				voice = await channel.connect()
				if "slow" in str(speed):
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=0.5" -vn'}
				elif "fast" in str(speed):
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=2" -vn'}
				else:
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=1" -vn'}
				voice.play(discord.FFmpegPCMAudio(source='https://cdn.discordapp.com/attachments/694603367531544617/865643189142159420/oldspice.mp3', **FFMPEG_OPTIONS))
				while voice.is_playing():
					await asyncio.sleep(1)
				if len(ctx.bot.voice_clients) != 0:
						await ctx.voice_client.disconnect()

	@commands.command(name='littleman')
	async def littleman(self, ctx, *speed):
		"""M A N L E T. Speed can be 'slow' or 'fast'. Must be in a voice channel."""

		if str(ctx.bot.voice_clients) == "[]":
			if ctx.author.voice == None:
				response = "You must be in a voice channel to use this command."
				await ctx.send(response)
			else:
				channel = ctx.author.voice.channel
				voice = await channel.connect()
				if "slow" in str(speed):
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=0.5" -vn'}
				elif "fast" in str(speed):
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=2" -vn'}
				else:
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=1" -vn'}
				voice.play(discord.FFmpegPCMAudio(source='https://cdn.discordapp.com/attachments/694603367531544617/865692091458781204/littleman.mp3', **FFMPEG_OPTIONS))
				while voice.is_playing():
					await asyncio.sleep(1)
				if len(ctx.bot.voice_clients) != 0:
					await ctx.voice_client.disconnect()

	@commands.command(name='totalquotes')
	async def totalquotes(self, ctx):
		"""Get the total number of quotes."""
		with open('quote_list.json', 'r') as f:
			data = json.load(f)
			maxIndex = 0
			for i in data:
				maxIndex = maxIndex + 1
			response = "My archives contain " + str(maxIndex) + " quotes."
					
		await ctx.send(response)

	@commands.command(name='bread')
	async def bread(self, ctx):
		"""B R E A D"""
		response = "🍞"
		await ctx.send(response)

	@commands.command(name='pain')
	async def pain(self, ctx):
		"""Hide the pain."""
		response = "<:harold:864874469818761216>"
		await ctx.send(response)

	@commands.command(name='play')
	async def play(self, ctx, URL: str, *speed):
		"""Play sounds. Speed can be 'slow' or 'fast'. Must be in a voice channel."""

		if str(ctx.bot.voice_clients) == "[]":
			if ctx.author.voice == None:
				response = "You must be in a voice channel to use this command."
				await ctx.send(response)
			else:
				channel = ctx.author.voice.channel
				voice = await channel.connect()
				if "slow" in str(speed):
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=0.5" -vn'}
				elif "fast" in str(speed):
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=2" -vn'}
				else:
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=1" -vn'}
				voice.play(discord.FFmpegPCMAudio(source=URL, **FFMPEG_OPTIONS))
				while voice.is_playing():
					await asyncio.sleep(1)
				if len(ctx.bot.voice_clients) != 0:
					await ctx.voice_client.disconnect()