import asyncio
import re
import subprocess
from hashlib import sha256

import nest_asyncio
import requests

nest_asyncio.apply()


async def generate_sha256(string: str) -> str:
	return sha256(string.encode('utf-8')).hexdigest()


def generate_sha256_no_async(string: str) -> str:
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


async def strip_usernames(user: str) -> str:
	return user.lstrip("<@!").rstrip(">")


def run_and_get(coro):
	loop = asyncio.get_event_loop()
	task = loop.create_task(coro)
	loop.run_until_complete(task)
	return task.result()


def run_and_get_new_loop(coro):
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)

	task = loop.create_task(coro)
	loop.run_until_complete(task)
	loop.close()
	return task.result()


def get_git_revision_short_hash() -> str:
	return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
