import importlib.util
import os

from Framework.CommandGroups.BasicCog import BasicCog
from Framework.ConfigurationManager import ConfigurationManager
from Framework.GeneralUtilities.ThreadedLogger import ThreadedLogger


class CustomCommandsLoader:

	def __init__(self):
		self.logger = ThreadedLogger("CustomCommandsLoader")
		self.path = f"{os.getcwd()}/Storage/CustomCommands"
		self.custom_cogs = []

		self.ensure_path_exists()

	def ensure_path_exists(self):
		if not os.path.exists(self.path):
			os.makedirs(self.path)

	def load_custom_cogs(self, bot, configuration_manager: ConfigurationManager):
		"""
		Load custom user cogs from the CustomCommands folder. Must extend BasicCog.
		"""
		for file in os.listdir(self.path):
			if file.endswith(".py") and file != "__init__.py":
				module_name = f"Storage.CustomCommands.{file[:-3]}"
				spec = importlib.util.spec_from_file_location(module_name, os.path.join(self.path, file))
				module = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(module)
				cog_class = getattr(module, file[:-3])

				# Check if the cog is a subclass of BasicCog
				if issubclass(cog_class, BasicCog):
					try:
						cog_instance = cog_class(bot, configuration_manager)
						self.custom_cogs.append(cog_instance)
						self.logger.log_debug(f"Loaded custom cog: {file[:-3]}")
					except Exception as e:
						self.logger.log_error(f"Error loading custom cog {file[:-3]}: {e}")
				else:
					raise Exception(f"Custom cog {file[:-3]} does not extend BasicCog")

		for cog in self.custom_cogs:
			bot.add_cog(cog)

	def unload_custom_cogs(self, bot):
		"""
		Unload all custom cogs from the bot.
		"""
		for cog in self.custom_cogs:
			bot.remove_cog(cog.qualified_name)
			self.logger.log_debug(f"Unloaded custom cog: {cog.qualified_name}")

		self.custom_cogs = []
