import ast
import multiprocessing
import re
from multiprocessing import Process

import js2py

from Framework.GeneralUtilities import Constants


################################################
# Osmium version v1.1.0 by AnonymousHacker1279 #
# All the files within these directories are   #
# MIT licensed.                                #
################################################


def execution_handler(js_code, response):
	response["result"] = None
	response["error"] = None

	try:
		response["result"] = str(js2py.eval_js(js_code))
	except js2py.PyJsException as error:
		response["error"] = "OSMIUM_ERROR: Failed to execute code. Reason:\n" + str(error)


class Osmium:

	def __init__(self, js_code: str = None, arguments: list = None, import_whitelist_location: str = None):
		self.error = None
		self.result = None

		self.arguments = arguments

		self.execution_time_remaining = Constants.CUSTOM_COMMANDS_MAX_EXECUTION_TIME
		self.execution_complete = False

		if import_whitelist_location is None:
			import_whitelist_location = "data/lists/import_whitelist.txt"

		with open(import_whitelist_location, "r") as f:
			self.whitelisted_imports = f.read()

		self.strip_imports(js_code)

	def strip_imports(self, js_code):
		split_code = js_code.split(';')
		for entry in split_code:
			if "pyimport" in entry:
				stripped_line = re.sub("pyimport ", "", entry)
				stripped_line = stripped_line.rstrip(';')
				if stripped_line not in self.whitelisted_imports:
					self.error = "OSMIUM_ERROR: Illegal import detected. Offending import: " + stripped_line

		if self.error is None:
			self.execute_js(js_code)

	def execute_js(self, js_code):
		js_code = self.inject(js_code)

		with multiprocessing.Manager() as manager:
			response = manager.dict()

			exec_process = Process(target=execution_handler, args=(js_code, response))
			exec_process.start()
			exec_process.join(Constants.CUSTOM_COMMANDS_MAX_EXECUTION_TIME)
			exec_process.terminate()

			try:
				if response["result"] is not None:
					self.result = ast.literal_eval(response["result"])
				self.error = response["error"]
			except ValueError:
				self.error = "OSMIUM_ERROR: Watchdog terminated execution because it took too much time. The maximum " \
							"execution time is " + str(Constants.CUSTOM_COMMANDS_MAX_EXECUTION_TIME) + " seconds."

			manager.shutdown()

	def inject(self, js_code):
		return """
		pyimport TBOsmiumLib;
		TBOsmiumLib.__purge_embed_dict__();
		TBOsmiumLib.__purge_arguments_list__();
		TBOsmiumLib.PASSED_ARGUMENTS = """ + str(self.arguments) + """
		""" + js_code + """
		var __OSMIUM_INTERNAL_RETURN__ = TBOsmiumLib.EMBED_FEATURES;
		"""
