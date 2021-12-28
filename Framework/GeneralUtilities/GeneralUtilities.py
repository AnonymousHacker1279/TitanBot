import os

def get_module_settings_directory():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/Modules.json")

def get_user_config_disabled_pings_directory():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/UserConfig/DisabledPings.json")

def get_quotes_directory():
	return os.path.abspath(os.getcwd() + "/Storage/Quotes.json")