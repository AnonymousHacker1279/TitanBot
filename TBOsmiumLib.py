#####################################################
# TBOsmiumLib version v1.1.0 by AnonymousHacker1279 #
# All the files within these directories are        #
# MIT licensed.                                     #
#####################################################


EMBED_FEATURES = {
	"title": "",
	"description": "",
	"image_url": "",
	"footer": "",
	"color": 0,
	"thumbnail_url": "",
	"author": {
		"name": "",
		"url": "",
		"image_url": ""
	},
	"fields": {
		"count": 0,
		"entries": {}
	}
}

PASSED_ARGUMENTS = []


# Internal functions
def __purge_embed_dict__():
	global EMBED_FEATURES
	EMBED_FEATURES = {
		"title": "",
		"description": "",
		"image_url": "",
		"footer": "",
		"color": 0,
		"thumbnail_url": "",
		"author": {
			"name": "",
			"url": "",
			"image_url": ""
		},
		"fields": {
			"count": 0,
			"entries": {}
		}
	}


def __purge_arguments_list__():
	global PASSED_ARGUMENTS
	PASSED_ARGUMENTS = []


def set_embed_title(title: str) -> str:
	EMBED_FEATURES["title"] = title
	return title


def get_embed_title() -> str:
	return EMBED_FEATURES["title"]


def set_embed_description(description: str) -> str:
	EMBED_FEATURES["description"] = description
	return description


def get_embed_description() -> str:
	return EMBED_FEATURES["description"]


def set_embed_image(image_url: str) -> str:
	stripped_url = strip_chevrons_from_url(image_url)
	EMBED_FEATURES["image_url"] = stripped_url
	return stripped_url


def get_embed_image() -> str:
	return EMBED_FEATURES["image_url"]


def set_embed_footer(footer: str) -> str:
	EMBED_FEATURES["footer"] = footer
	return footer


def get_embed_footer() -> str:
	return EMBED_FEATURES["footer"]


def set_embed_color(decimal_code: int) -> int:
	EMBED_FEATURES["color"] = decimal_code
	return decimal_code


def get_embed_color() -> int:
	return EMBED_FEATURES["color"]


def set_embed_thumbnail(image_url: str) -> str:
	stripped_url = strip_chevrons_from_url(image_url)
	EMBED_FEATURES["thumbnail_url"] = stripped_url
	return stripped_url


def get_embed_thumbnail() -> str:
	return EMBED_FEATURES["thumbnail_url"]


def set_embed_author(author_name: str, author_url: str = "", image_url: str = "") -> dict[str, str, str]:
	stripped_author_url = strip_chevrons_from_url(author_url)
	stripped_image_url = strip_chevrons_from_url(image_url)
	EMBED_FEATURES["author"]["name"] = author_name
	EMBED_FEATURES["author"]["url"] = stripped_author_url
	EMBED_FEATURES["author"]["image_url"] = stripped_image_url
	return EMBED_FEATURES["author"]


def get_embed_author() -> dict[str, str, str]:
	return EMBED_FEATURES["author"]


def add_embed_field(name: str, value: str, inline: bool = True) -> [str, str, bool]:
	EMBED_FEATURES["fields"]["entries"][name] = {
		"value": value,
		"inline": inline
	}
	EMBED_FEATURES["fields"]["count"] = EMBED_FEATURES["fields"]["count"] + 1
	return name, value, inline


def remove_embed_field(name: str):
	if EMBED_FEATURES["fields"]["count"] != 0:
		EMBED_FEATURES["fields"]["entries"].pop(name)
		EMBED_FEATURES["fields"]["count"] = EMBED_FEATURES["fields"]["count"] - 1


def get_embed_field_count() -> int:
	return EMBED_FEATURES["fields"]["count"]


def get_arguments() -> list:
	return PASSED_ARGUMENTS


# Helper functions go here

def get_version() -> str:
	return "v1.1.0"


def strip_chevrons_from_url(url: str) -> str:
	return url.lstrip('<').rstrip('>')


def hex_to_decimal(hex_code: str) -> int:
	hex_code = hex_code.lstrip('#')
	return int(hex_code, 16)


def rgb_to_decimal(r: int, g: int, b: int) -> int:
	return (r << 16) + (g << 8) + b
