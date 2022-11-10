import ast
import re
import threading
from multiprocessing import Process

import js2py


def execution_handler(js_code, response):
	"""
	Execute the JS code and store the result in the shared dict. Intended to be run in a separate process.
	"""

	try:
		response["result"] = str(js2py.eval_js(js_code))
	except js2py.PyJsException as error:
		response["error"] = "OSMIUM_ERROR: Failed to execute code. Reason:\n" + str(error)


async def strip_imports(js_code: str, whitelisted_imports: str):
	"""
	Check the imports for anything not on the whitelist.
	"""
	split_code = js_code.split(';')
	for entry in split_code:
		if "pyimport" in entry:
			stripped_line = re.sub("pyimport ", "", entry)
			stripped_line = stripped_line.rstrip(';')
			if stripped_line not in whitelisted_imports:
				return "OSMIUM_ERROR: Illegal import detected. Offending import: " + stripped_line
	return None


async def execute_js(js_code: str, response, max_execution_time: int):
	"""Execute the JS code in a separate process."""
	p = Process(target=execution_handler, args=(js_code, response), daemon=True, name="Osmium Execution Handler")
	p.start()
	# Do not use p.join() as it will block the main thread. Make a new thread which will wait for the process to finish.
	# This is done so that the main thread can still handle other requests.
	threading.Thread(target=wait_for_process, args=(p, max_execution_time, response), daemon=True, name="Osmium Process Watchdog").start()


def wait_for_process(p, max_execution_time, response):
	"""
	Wait for the process to finish or timeout.
	"""
	p.join(max_execution_time)
	if p.is_alive():
		p.terminate()
		p.join()

	response["error"] = "OSMIUM_ERROR: Watchdog terminated execution because it took too much time. The maximum " \
						"execution time is " + str(max_execution_time) + " seconds."


async def inject(js_code, arguments):
	"""
	Inject header and footer data.
	This imports TBOsmiumLib, clears the previous embed and arg variables, then sets the return action.
	"""
	return """
		pyimport TBOsmiumLib;
		TBOsmiumLib.__purge_embed_dict__();
		TBOsmiumLib.__purge_arguments_list__();
		TBOsmiumLib.PASSED_ARGUMENTS = """ + str(arguments) + """
		""" + js_code + """
		var __OSMIUM_INTERNAL_RETURN__ = TBOsmiumLib.EMBED_FEATURES;
		"""