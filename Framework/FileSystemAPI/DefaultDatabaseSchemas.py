async def get_modules_schema() -> dict:
	return {
		"moduleConfiguration": {
			"quotes": {
				"enabled": True,
				"forceEnabled": False,
				"displayName": "Quotes",
				"id": "quotes",
				"description": "The quote system allows users to remember the silly stuff they say.",
				"commands": [
					"quote",
					"add_quote",
					"remove_quote",
					"total_quotes",
					"search_quotes_author",
					"search_quotes_text"
				]
			},
			"fun": {
				"enabled": True,
				"forceEnabled": False,
				"displayName": "Fun",
				"id": "fun",
				"description": "The 'Fun' system simply allows users to mess with each other.",
				"commands": [
					"stab",
					"spotify"
				]
			},
			"utility": {
				"enabled": True,
				"forceEnabled": False,
				"displayName": "Utility",
				"id": "utility",
				"description": "The utility system provides useful tools and functionalities.",
				"commands": [
					"about",
					"age",
					"flip_coin",
					"roll_die",
					"status",
					"total_users",
					"ping"
				]
			},
			"genius": {
				"enabled": True,
				"forceEnabled": False,
				"displayName": "Genius",
				"id": "genius",
				"description": "The Genius system allows you to interact with the Genius music API.",
				"commands": [
					"search_songs",
					"get_lyrics_by_url",
					"get_lyrics_by_id"
				]
			},
			"customCommands": {
				"enabled": True,
				"forceEnabled": False,
				"displayName": "Custom Commands",
				"id": "customCommands",
				"description": "The Custom Commands system allows you to expand the power of TitanBot by implementing your own features on-the-fly without modifying bot code.",
				"commands": [
					"custom_command",
					"add_command",
					"remove_command",
					"command_info"
				]
			},
			"moderator": {
				"enabled": True,
				"forceEnabled": False,
				"displayName": "Moderator",
				"id": "moderator",
				"description": "The moderator system provides management commands to users with adequate permissions.",
				"commands": [
					"revoke_command_access",
					"view_revoked_commands",
					"revoke_module_access",
					"view_revoked_modules"
				]
			}
		}
	}


async def get_custom_commands_metadata_schema() -> dict:
	return {
		"metadata": {},
		"aliases": {},
		"wizard_only_commands": []
	}


async def get_storage_metadata_schema() -> dict:
	return {
		"metadata_version": 1,
		"guilds": {}
	}


async def get_empty_schema() -> list:
	return []

