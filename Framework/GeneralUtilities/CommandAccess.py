from ..GeneralUtilities import GeneralUtilities as Utilities
import json

class CommandAccess():
	
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