import ast
import multiprocessing
import re
import threading
import time
from datetime import datetime
from multiprocessing import Process

import js2py

from Framework.GeneralUtilities import GeneralUtilities


################################################
# Osmium version v1.1.1 by AnonymousHacker1279 #
################################################


def execution_handler(js_code, response):
	response["result"] = None
	response["error"] = None

	try:
		response["result"] = str(js2py.eval_js(js_code))
	except js2py.PyJsException as error:
		response["error"] = "OSMIUM_ERROR: Failed to execute code. Reason:\n" + str(error)


class Osmium:

	def __init__(self, management_portal_handler, guild_id: int, js_code: str = None, arguments: list = None, import_whitelist_location: str = None):
		self.error = None
		self.result = None

		self.guild_id = guild_id
		self.mph = management_portal_handler
		self.arguments = arguments

		if import_whitelist_location is None:
			import_whitelist_location = "data/lists/import_whitelist.txt"

		with open(import_whitelist_location, "r") as f:
			self.whitelisted_imports = f.read()

		GeneralUtilities.run_and_get(self.strip_imports(js_code))

	async def strip_imports(self, js_code):
		split_code = js_code.split(';')
		for entry in split_code:
			if "pyimport" in entry:
				stripped_line = re.sub("pyimport ", "", entry)
				stripped_line = stripped_line.rstrip(';')
				if stripped_line not in self.whitelisted_imports:
					self.error = "OSMIUM_ERROR: Illegal import detected. Offending import: " + stripped_line

		if self.error is None:
			await self.execute_js(js_code)

	async def execute_js(self, js_code):
		js_code = await self.inject(js_code)

		max_exec_time = await self.mph.cm.get_guild_specific_value(self.guild_id, "custom_commands_max_execution_time")

		# Make a shared dict to store the result and error
		manager = multiprocessing.Manager()
		response = manager.dict()

		p = Process(target=execution_handler, args=(js_code, response))
		p.start()
		p.join(max_exec_time)

		if p.is_alive():
			p.terminate()
			p.join()

		try:
			if response["result"] is not None:
				self.result = ast.literal_eval(response["result"])
			self.error = response["error"]
		except ValueError:
			self.error = "OSMIUM_ERROR: Watchdog terminated execution because it took too much time. The maximum " \
						"execution time is " + str(max_exec_time) + " seconds."

	async def inject(self, js_code):
		return """
		pyimport TBOsmiumLib;
		TBOsmiumLib.__purge_embed_dict__();
		TBOsmiumLib.__purge_arguments_list__();
		TBOsmiumLib.PASSED_ARGUMENTS = """ + str(self.arguments) + """
		""" + js_code + """
		var __OSMIUM_INTERNAL_RETURN__ = TBOsmiumLib.EMBED_FEATURES;
		"""
