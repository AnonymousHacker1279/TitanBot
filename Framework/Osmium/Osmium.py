import ast
import multiprocessing

from Framework.FileSystemAPI.ThreadedLogger import ThreadedLogger
from Framework.Osmium import OsmiumFunctions


class Osmium:

	def __init__(self, management_portal_handler):
		self.logger = ThreadedLogger("Osmium", management_portal_handler)
		self.functions = OsmiumFunctions
		self.process_manager = multiprocessing.Manager()

		self.whitelisted_imports = ""

	async def set_import_whitelist(self, whitelist: str):
		self.whitelisted_imports = whitelist

	async def execute(self, js_code: str, arguments: list, max_execution_time: int):
		error = await self.functions.strip_imports(js_code, self.whitelisted_imports)

		if error is not None:
			return error

		injected_js_code = await self.functions.inject(js_code, arguments)

		response = self.process_manager.dict()

		response["result"] = None
		response["error"] = None

		await self.functions.execute_js(injected_js_code, response, max_execution_time)

		# Wait for the process to finish
		while response["result"] is None and response["error"] is None:
			pass

		if response["result"] is not None:
			result = ast.literal_eval(response["result"])
		else:
			result = None

		return result, response["error"]
