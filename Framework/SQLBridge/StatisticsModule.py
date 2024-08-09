import sqlite3


class StatisticsModule:

	def __init__(self, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
		self.connection = connection
		self.cursor = cursor

	async def get_top_ten_commands(self) -> list:
		"""Get the top ten most used commands."""

		self.cursor.execute("""
			SELECT command_name, module_name, count
			FROM command_usage_analytics
			ORDER BY count DESC
			LIMIT 10
		""")

		return self.cursor.fetchall()
