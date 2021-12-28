from ..GeneralUtilities import GeneralUtilities as Utilities
import json
from discord import utils
from dotenv import load_dotenv
import os

class CommandAccess():

	load_dotenv()
	WIZARD_ROLE = os.getenv('WIZARD_ROLE')
	
	async def check_module_enabled(module):
		# Open the settings file
		with open(Utilities.get_module_settings_directory(), 'r') as f:
			data = json.load(f)

			# Get status
			return data["moduleConfiguration"][module]["enabled"]

	async def check_user_pings(user):
		# Open the settings file
		with open(Utilities.get_user_config_disabled_pings_directory(), 'r') as f:
			data = json.load(f)

			# Check if the user is in the disabled pings list
			return user in data["disabledPings"]

	async def check_user_is_wizard(ctx):
		# Check if a user is a wizard
		# The "wizard" check ensures that a user has permissions
		#  to use moderator-level commands.
		return utils.get(ctx.author.roles, id=int(CommandAccess.WIZARD_ROLE))
