async def is_superuser(mph, user: int) -> bool:
	# Check if a user is a superuser
	superusers = await mph.cm.get_value("superuser_list")
	return str(user) in superusers


async def check_module_enabled(mph, module: str, guild: int) -> bool:
	enabled_modules = await mph.cm.get_guild_specific_value(guild, "enabled_modules")
	return enabled_modules[module + "_enabled"]


async def check_user_is_banned_from_command(mph, user: int, command: str, guild: int) -> bool:
	# Check if a user is banned from using a command
	banned_commands = await mph.access_control.get_banned_commands(user, guild)
	return command in banned_commands


async def check_user_is_banned_from_module(mph, user: int, module: str, guild: int) -> bool:
	# Check if a user is banned from using a module
	banned_modules = await mph.access_control.get_banned_modules(user, guild)
	return module in banned_modules
