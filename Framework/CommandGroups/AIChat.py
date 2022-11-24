import asyncio
import os
import random
import threading
import time
from queue import Queue

import discord
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from discord.ext import commands, tasks
from discord.ext.bridge import bot

from ..FileSystemAPI import DatabaseObjects
from ..FileSystemAPI.CacheManager.DatabaseCacheManager import DatabaseCacheManager
from ..FileSystemAPI.ThreadedLogger import ThreadedLogger
from ..GeneralUtilities import PermissionHandler
from ..ManagementPortal.ManagementPortalHandler import ManagementPortalHandler


class AIChat(commands.Cog):
	"""Talk to the bot, and it will try to respond with AI."""

	def __init__(self, management_portal_handler: ManagementPortalHandler, logger: ThreadedLogger):
		self.mph = management_portal_handler
		self.bot = management_portal_handler.bot
		self.logger = logger

		self.chat_settings = {}
		self.cache_manager = {}
		self.message_processing_queue = Queue()
		self.send_pending_messages_queue = Queue()

		self.train_corpus = True
		if os.path.exists(os.getcwd() + "\\Storage\\ai_chat_database.sqlite3"):
			self.train_corpus = False

		self.chatbot = ChatBot('TitanBot',
								storage_adapter={'import_path': 'chatterbot.storage.SQLStorageAdapter',
												'database_uri': 'sqlite:///Storage/ai_chat_database.sqlite3'})
		self.corpus_trainer = ChatterBotCorpusTrainer(self.chatbot, show_training_progress=False)
		self.list_trainer = ListTrainer(self.chatbot, show_training_progress=False)
		self.training_complete = threading.Event()

	async def post_initialize(self):
		for guild in self.mph.bot.guilds:
			self.chat_settings[guild.id] = {"enabled": False,
											"channel": None,
											"minutes_remaining": 0,
											"train_only": False}

		self.cache_manager = DatabaseCacheManager("ai_chat_learned_words",
												management_portal_handler=self.mph,
												guild_id=-1,
												path_to_database=await DatabaseObjects.get_ai_chat_learned_content_database())

		# Train with the English corpus in a new thread
		self.logger.log_info("Training AI chat responses...")

		threading.Thread(
				target=self.train_chatbot,
				args=(self.corpus_trainer, self.list_trainer, self.logger, self.cache_manager, self.train_corpus, self.training_complete),
				daemon=True,
				name="AI Chat Trainer").start()

		threading.Thread(
				target=self.get_chatbot_response,
				args=(self.chatbot, self.message_processing_queue, self.send_pending_messages_queue),
				daemon=True,
				name="AI Chat Responder").start()

		self.tick_minutes_remaining.start()
		self.send_pending_messages.start()

	def train_chatbot(self, corpus_trainer, list_trainer, logger, cache_manager, should_train_corpus, training_complete):
		"""Train the chatbot with the English corpus and any learned phrases."""

		# Create a new event loop for the thread
		asyncio.set_event_loop(asyncio.new_event_loop())

		if should_train_corpus:
			logger.log_info("Training on the English corpus...")
			corpus_trainer.train("chatterbot.corpus.english")

		self.train_learned_responses(list_trainer, logger, cache_manager)

		logger.log_info("Training complete")

		training_complete.set()

	def train_learned_responses(self, list_trainer, logger, cache_manager):
		logger.log_info("Training on learned words...")
		cache = asyncio.run(cache_manager.get_cache())
		learned_content = cache["learned_content"].copy()
		random.shuffle(learned_content)
		list_trainer.train(learned_content)

	def get_chatbot_response(self, chatbot, incoming_queue, outgoing_queue):
		"""Get the chatbot response to a message."""

		while True:
			if not incoming_queue.empty():
				entry = incoming_queue.get()
				message = entry["content"]
				settings = entry["settings"]

				response = chatbot.get_response(message)
				outgoing_queue.put({"response": response, "settings": settings})

				incoming_queue.task_done()

			time.sleep(0.1)

	@bot.bridge_command()
	@commands.guild_only()
	async def enable_chatting(self, ctx: discord.ApplicationContext, channel: discord.TextChannel, minutes: int = 5, train_only: bool = False):
		"""Enable AI responses when you talk."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "ai_chat", "enable_chatting")
		if not failedPermissionCheck:
			if self.training_complete.is_set():
				self.chat_settings[ctx.guild.id]["enabled"] = True
				self.chat_settings[ctx.guild.id]["channel"] = channel
				self.chat_settings[ctx.guild.id]["minutes_remaining"] = minutes
				self.chat_settings[ctx.guild.id]["train_only"] = train_only

				embed.title = "AI Chat Response Enabled"
				embed.description = "AI Chat Response is now enabled.\n" + f"It will be disabled in {minutes} minutes."
				if train_only:
					embed.description += "\n\nThis is a training-only session. No responses will be sent."
			else:
				embed.title = "AI Chat Response Cannot Be Enabled"
				embed.description = "The bot is still training its AI responses. Please try again in a few minutes."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("ai_chat", "enable_chatting", ctx.guild.id)

	@bot.bridge_command()
	@commands.guild_only()
	async def disable_chatting(self, ctx: discord.ApplicationContext):
		"""Disable AI responses when you talk."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "ai_chat", "disable_chatting")
		if not failedPermissionCheck:
			self.chat_settings[ctx.guild.id]["enabled"] = False
			self.chat_settings[ctx.guild.id]["channel"] = None
			self.chat_settings[ctx.guild.id]["minutes_remaining"] = 0

			embed.title = "AI Chat Response Disabled"
			embed.description = "AI Chat Response is now disabled."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("ai_chat", "disable_chatting", ctx.guild.id)

	@bot.bridge_command()
	@commands.guild_only()
	async def force_retrain(self, ctx: discord.ApplicationContext):
		"""Force the bot to retrain its AI responses."""

		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed, failedPermissionCheck = await PermissionHandler.check_permissions(ctx, embed, "ai_chat", "force_retrain", True)
		if not failedPermissionCheck:
			self.logger.log_info("Retraining AI chat responses...")
			threading.Thread(
					target=self.train_learned_responses,
					args=(self.list_trainer, self.logger, self.cache_manager),
					daemon=True,
					name="AI Chat Trainer").start()

			embed.title = "AI Chat Response Retraining"
			embed.description = "The bot is now retraining its responses."

		await ctx.respond(embed=embed)
		await self.mph.update_management_portal_command_used("ai_chat", "force_retrain", ctx.guild.id)

	@tasks.loop(minutes=1)
	async def tick_minutes_remaining(self):
		for guild_id in self.chat_settings:
			if self.chat_settings[guild_id]["enabled"]:
				self.chat_settings[guild_id]["minutes_remaining"] -= 1

				if self.chat_settings[guild_id]["minutes_remaining"] <= 0:
					self.chat_settings[guild_id]["enabled"] = False
					self.chat_settings[guild_id]["minutes_remaining"] = 0

					channel = self.chat_settings[guild_id]["channel"]

					embed = discord.Embed(color=discord.Color.dark_blue(),
										title="AI Chat Response Disabled",
										description="Responses have automatically been disabled as the time limit has been met.")
					await channel.send(embed=embed)

	@tasks.loop(seconds=0.5)
	async def send_pending_messages(self):
		while not self.send_pending_messages_queue.empty():
			entry = self.send_pending_messages_queue.get()
			response = entry["response"]
			settings = entry["settings"]

			await settings["channel"].send(response)

			self.send_pending_messages_queue.task_done()

	async def handle_message_event(self, message: discord.Message):
		if self.chat_settings == {}:
			return

		if self.chat_settings[message.guild.id]["enabled"] and message.channel == self.chat_settings[message.guild.id]["channel"]:

			if message.content == "":
				return

			if not self.chat_settings[message.guild.id]["train_only"]:
				await message.channel.trigger_typing()
				self.message_processing_queue.put(
						{"content": message.content, "settings": self.chat_settings[message.guild.id]})

			cache = await self.cache_manager.get_cache()
			cache = cache["learned_content"]

			if message.content not in cache:
				cache.append(message.content)
				await self.cache_manager.sync_cache_to_disk()
