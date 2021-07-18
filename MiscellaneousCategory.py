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

	@commands.command(name='slap')
	async def slap(self, ctx, *slappable: str):
		"""You can finally slap someone through the internet."""
		with open('bot_actions_after_shot.json', 'r') as f:
			data = json.load(f)
			maxIndex = 0
			for i in data:
				maxIndex = maxIndex + 1
			random = randint(0, maxIndex - 1)
		if str(slappable) == "()":
			response = "Well, are you going to slap someone or not?"
		elif "(''," in str(slappable).translate({ord(i): None for i in '*'}):
			response = "Try again when you can coherently form a word."
		elif "<@!865380885649031178>" in str('{}'.format(' '.join(slappable).replace('*', ''))):
			response = "*" + str(ctx.message.author.mention) + " was shot by " + str(ctx.bot.user.mention) + " while " + str(data[random - 1]["content"]) + "*"
		elif "<@!417794810284474378>" in str('{}'.format(' '.join(slappable).replace('*', ''))) or "<@!509490815236833280>" in str('{}'.format(' '.join(slappable).replace('*', ''))) or "<@!567446167827513350>" in str('{}'.format(' '.join(slappable).replace('*', ''))):
			response = "*" + str(ctx.bot.user.mention) + " intervened and shot " + str('{}'.format(' '.join(slappable).replace('*', ''))) + " while " + str(data[random - 1]["content"]) + "*"
		else:
			response = "*" + str('{}'.format(' '.join(slappable).replace('*', ''))) + " was slapped by " + str(ctx.message.author.mention) + " at Mach " + str(randint(1,9)) + ". They started crying.*".lstrip(" ")
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

		isBanned = False
		with open('noquote_users.json', 'r') as f:
			data = json.load(f)
			maxIndex = 0
			userIndex = None
			modifiedUserMention = str(ctx.message.author.mention)[ : 2] + "!" + str(ctx.message.author.mention)[2 : ]
			print(modifiedUserMention)
			for i in data:
				maxIndex = maxIndex + 1
				if str(modifiedUserMention) in i['user']:
					userIndex = maxIndex
			if userIndex != None:
				isBanned = True

		if isBanned == False:
			with open('quote_list.json', 'r') as f:
				data = json.load(f)
			
			with open('quote_list.json', 'w') as f:
				quoteDictionary = {"content": str('{}'.format(' '.join(quote))) , "author": str(author)}
				data = list(data)
				data.append(quoteDictionary)
				json.dump(data, f, indent=4)
			
			response = "Added quote to archive."
		else:
			response = "You're not allowed to add quotes. Peasant."
		
		await ctx.send(response)

	@commands.command(name='searchquotes')
	async def searchquotes(self, ctx, author: str, page=1):
		"""Search for quotes by author. Additionally, pass the page number. Five quotes per page are displayed."""

		# Open JSON list
		with open('quote_list.json', 'r') as f:
			data = json.load(f)
			maxIndex = 0
			authorQuoteIndex = []
			# Get the maximum index, and an index of all the author's quotes
			for i in data:
				maxIndex = maxIndex + 1
				if author in i['author']:
					authorQuoteIndex.append(maxIndex)
			# First line of response: Author + total quotes
			response = ">>> " + author + " is currently credited with **" + str(len(authorQuoteIndex)) + "** quotes.\n"
			# Check if first page
			if page == 1:
				if len(authorQuoteIndex) != 0:
					# List the first 5 quotes if the length of the index isn't zero
					response += "Listing the first five quotes by this author: \n\n"
					iteration = 0
					# Iterate through the index and build a response
					for i in authorQuoteIndex:
						response += data[authorQuoteIndex[iteration] - 1]["content"] + " **Quote #" + str(authorQuoteIndex[iteration]) + "**\n"
						iteration = iteration + 1
						if iteration >= 5:
							break
			else:
				# Check if there are enough quotes to fill a page
				if len(authorQuoteIndex) <= 5 or len(authorQuoteIndex) <= (page - 1 * 5):
					response += "This author doesn't have enough quotes to reach this page."
				else:
					# List the next 5 by page number
					response += "Listing the next five quotes by this author (**Page " + str(page) + "**): \n\n"
					# Set the iteration by multiplying the page number by 5. First, shift left 1 (as indexes start at 0)
					iteration = (page - 1) * 5
					# Iterate through the index and build a response
					for i in authorQuoteIndex:
						response += data[authorQuoteIndex[iteration] - 1]["content"] + " **Quote #" + str(authorQuoteIndex[iteration]) + "**\n"
						iteration = iteration + 1
						if iteration >= 5:
							break
		# Send response
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
	async def bruh(self, ctx, *speed):
		"""Bruh moment. Speed can be 'realslow', 'slow' or 'fast'. Must be in a voice channel."""
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
				elif "realslow" in str(speed):
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=0.5,atempo=0.5" -vn'}
				else:
					FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-filter:a "atempo=1" -vn'}
				voice.play(discord.FFmpegPCMAudio(source='https://cdn.discordapp.com/attachments/694603367531544617/865641424665837618/Bruh_Sound_Effect_2.mp3', **FFMPEG_OPTIONS))
				while voice.is_playing():
					await asyncio.sleep(1)
				if len(ctx.bot.voice_clients) != 0:
					await ctx.voice_client.disconnect()

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