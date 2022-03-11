import os


def get_module_settings_database():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/Modules.json")


def get_user_config_disabled_pings_database():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/UserConfig/DisabledPings.json")


def get_quotes_database():
	return os.path.abspath(os.getcwd() + "/Storage/Quotes.json")


def get_revoked_commands_database():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/UserAccess/Commands/RevokedCommands.json")


def get_revoked_modules_database():
	return os.path.abspath(os.getcwd() + "/Storage/Settings/UserAccess/Modules/RevokedModules.json")


def get_custom_commands_directory():
	return os.path.abspath(os.getcwd() + "/Storage/CustomCommands")


def get_custom_commands_alias_database():
	return os.path.abspath(os.getcwd() + "/Storage/CustomCommands/aliases.json")
