import os
import re
from hashlib import sha256

import requests


async def get_module_settings_database():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/Modules.json")


async def get_user_config_disabled_pings_database():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/UserConfig/DisabledPings.json")


async def get_quotes_database():
	return os.path.abspath(os.getcwd() + "/Storage/Quotes.json")


async def get_revoked_commands_database():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/UserAccess/Commands/RevokedCommands.json")


async def get_revoked_modules_database():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/UserAccess/Modules/RevokedModules.json")


async def get_custom_commands_directory():
	return os.path.abspath(os.getcwd() + "/Storage/CustomCommands")


async def get_custom_commands_metadata_database():
	return os.path.abspath(os.getcwd() + "/Storage/CustomCommands/metadata.json")


async def generate_sha256(string: str) -> str:
	return sha256(string.encode('utf-8')).hexdigest()


async def minimize_js(code: str) -> str:
	# Need to remove all import statements before minimization, since it isn't true JS
	import_items = re.findall(re.compile(r"pyimport [a-z0-9]*;"), code)
	js = code
	for item in import_items:
		js = js.replace(item, "")

	js = requests.post('https://www.toptal.com/developers/javascript-minifier/raw', data={"input": js}).text

	# Put the imports back at the beginning
	for item in import_items:
		js = item + js

	return js
