from enum import Enum


class APIEndpoints(str, Enum):
	UPDATE_LATENCY = "/v2/bot_update_latency.php"
	LOG_DATA = "/v2/bot_log_data.php"
	UPDATE_COMMAND_COMPLETED = "/v2/bot_update_command_completed.php"
	GET_CONFIGURATION = "/v3/configurations/portal_get_configuration.php"
	WRITE_CONFIGURATION = "/v3/configurations/bot_write_configuration.php"
	MIGRATE_QUOTES = "/v2/migrations/migrate_quotes.php"
	GET_QUOTE = "/v2/modules/quotes/get_quote.php"
	ADD_QUOTE = "/v2/modules/quotes/add_quote.php"
	REMOVE_QUOTE = "/v2/modules/quotes/remove_quote.php"
	GET_QUOTE_COUNT = "/v2/modules/quotes/get_quote_count.php"
	EDIT_QUOTE = "/v2/modules/quotes/edit_quote.php"
	SEARCH_QUOTES = "/v2/modules/quotes/search_quotes.php"
	LIST_RECENT_QUOTES = "/v2/modules/quotes/list_recent_quotes.php"
	MODIFY_CF_UPDATE_CHECKER = "/v3/modules/curseforge/modify_project.php"
	GET_CF_PROJECTS = "/v3/modules/curseforge/get_projects.php"
	UPDATE_CF_PROJECT = "/v3/modules/curseforge/update_project.php"
	GET_COMMAND_USAGE_ANALYTICS = "/v3/modules/statistics/get_command_usage_analytics.php"
