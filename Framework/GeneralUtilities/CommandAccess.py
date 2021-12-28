from ..GeneralUtilities import GeneralUtilities as Utilities
import json

class CommandAccess():
	
	async def check_module_enabled(module):
		# Open the settings file
		with open(Utilities.get_module_settings_directory(), 'r') as f:
			data = json.load(f)

			# Get status
			return data["moduleConfiguration"][module]["enabled"]