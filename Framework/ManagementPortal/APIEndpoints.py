from enum import Enum


class APIEndpoints(str, Enum):
	GET_CONFIGURATION = "/v3/configurations/portal_get_configuration.php"
	WRITE_CONFIGURATION = "/v3/configurations/bot_write_configuration.php"
