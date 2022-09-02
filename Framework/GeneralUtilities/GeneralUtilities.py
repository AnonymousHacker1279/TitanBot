import re
from hashlib import sha256

import requests


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


async def arg_splitter(message: str) -> list:
	last = 0
	args = []
	in_quote = None
	for iteration, character in enumerate(message):
		if in_quote:
			if character == in_quote:
				in_quote = None
		else:
			if character == '"' or character == "'":
				in_quote = character

		if not in_quote and character == ' ':
			args.append(message[last:iteration])
			last = iteration + 1

	if last < len(message):
		args.append(message[last:])

	for iteration, item in enumerate(args):
		args[iteration] = item.rstrip("'").rstrip('"').lstrip("'").lstrip('"')

	return args
