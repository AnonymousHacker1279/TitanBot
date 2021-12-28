import json
from discord.ext import commands
import discord
from ..GeneralUtilities import GeneralUtilities as Utilities
from ..GeneralUtilities.CommandAccess import CommandAccess

class ModuleSystem(commands.Cog):

	@commands.command(name='moduleInfo')
	@commands.guild_only()
	async def module_info(self, ctx, module=None):
		"""Get module information. Lists all modules and their status by default. Specify a specific module to get detailed information."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')
		embed.title = "Module System: Information"

		# Open the settings file
		with open(Utilities.get_module_settings_directory(), 'r') as f:
			data = json.load(f)

			# Initialize variables
			totalModules = 0
			moduleList = []

			# Get the total modules and build a list
			for i in data["moduleConfiguration"]:
				totalModules = totalModules + 1
				moduleList.append(i)

			# Default action
			if module == None:
				embed.description += "Total Modules: " + str(totalModules) + "\n"

				# For each item in the module list, get the display name and its status
				for i in moduleList:
					line = " - " + data["moduleConfiguration"][i]["displayName"] + " Module (" + data["moduleConfiguration"][i]["id"] + "): "
					if data["moduleConfiguration"][i]["enabled"] == True:
						line += "Enabled :white_check_mark:"
					else:
						line += "Disabled :negative_squared_cross_mark:"
					embed.description += line + "\n"
			# Check if the module is in the list
			elif module in str(moduleList):
				# Set the title with the module display name
				embed.title = "Module System: Information - " + data["moduleConfiguration"][module]["displayName"]
				# Get status
				if data["moduleConfiguration"][module]["enabled"] == True:
					line = "Enabled :white_check_mark:"
				else:
					line = "Disabled :negative_squared_cross_mark:"
				embed.description += line + "\n"
				if data["moduleConfiguration"][module]["forceEnabled"] == True:
					embed.description += "**This module is force enabled, and cannot be disabled via commands.**\n"
				# Get description
				embed.description += "Description: *" + data["moduleConfiguration"][module]["description"] + "*\n"
				# Get commands
				embed.description += "Commands: " + str(data["moduleConfiguration"][module]["commands"]) + "\n"
			else:
				# No module was found, so let the user know
				embed.description = "No module was found of the ID '" + str(module) + "'"

		await ctx.send(embed = embed)

	@commands.command(name='toggleModuleState')
	@commands.guild_only()
	async def toggle_module_state(self, ctx, module=None):
		"""Toggle the state of a module. Pass the ID of the module you wish to toggle."""
		embed = discord.Embed(color=discord.Color.dark_blue(), description='')

		if await CommandAccess.check_user_is_wizard(ctx) == None:
			embed.title = "Cannot use this command"
			embed.description = "You do not have access to use this command."

		embed.title = "Module System: Toggle Module State"

		# Open the settings file
		with open(Utilities.get_module_settings_directory(), 'r') as f:
			data = json.load(f)

		# Initialize variables
		totalModules = 0
		moduleList = []

		# Get the total modules and build a list
		for i in data["moduleConfiguration"]:
			totalModules = totalModules + 1
			moduleList.append(i)

		# Default action
		if module == None:
			# No module was specified, so throw an error.
			embed.description = "No module was specified. "
		# Check if the module is in the list
		elif module in str(moduleList):
			# Check if the module is force enabled
			if data["moduleConfiguration"][module]["forceEnabled"] == True:
				embed.title = "Module System: Failed to toggle state of " + data["moduleConfiguration"][module]["displayName"]
				embed.description = "This module is force enabled, and cannot be disabled via commands."
			else:
				# Set the title with the module display name
				embed.title = "Module System: Toggled state of " + data["moduleConfiguration"][module]["displayName"]
				# Toggle the state of the module
				if data["moduleConfiguration"][module]["enabled"] == True:
					data["moduleConfiguration"][module]["enabled"] = False
					line = "The module state has changed. New state:\nDisabled :negative_squared_cross_mark:"
				else:
					data["moduleConfiguration"][module]["enabled"] = True
					line = "The module state has changed. New state:\nEnabled :white_check_mark:"
				with open(Utilities.get_module_settings_directory(), 'w') as f:
					json.dump(data, f, indent=4)
				embed.description += line + "\n"
		else:
			# No module was found, so let the user know
			embed.description = "No module was found of the name '" + str(module) + "'"

		await ctx.send(embed = embed)