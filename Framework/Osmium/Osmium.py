import js2py
import re

################################################
# Osmium version v1.0.0 by AnonymousHacker1279 #
# All the files within these directories are   #
# MIT licensed.                                #
################################################


class Osmium:

	def __init__(self, js_code, import_whitelist_location=None):
		self.error = None
		self.result = None

		if import_whitelist_location is None:
			import_whitelist_location = "data/lists/import_whitelist.txt"

		with open(import_whitelist_location, "r") as f:
			self.whitelisted_imports = f.read()

		self.strip_imports(js_code)

	def strip_imports(self, js_code):
		for line in js_code.splitlines():
			if "pyimport" in line:
				stripped_line = re.sub("pyimport ", "", line)
				if stripped_line not in self.whitelisted_imports:
					self.error = "OSMIUM_ERROR: Illegal import detected. Offending import: " + stripped_line

		if self.error is None:
			self.strip_newlines(js_code)

	def strip_newlines(self, js_code):
		js_code = js_code.replace('\n', '')

		if self.error is None:
			self.execute_js(js_code)

	def execute_js(self, js_code):
		js_code = self.inject_libs(js_code)
		try:
			self.result = js2py.eval_js(js_code)
		except js2py.PyJsException as error:
			self.error = "OSMIUM_ERROR: Failed to execute code. Reason:\n" + str(error)

	def inject_libs(self, js_code):
		return """
		pyimport TBOsmiumLib;
		""" + js_code + """
		var __OSMIUM_INTERNAL_RETURN__ = TBOsmiumLib.EMBED_FEATURES;
		"""
