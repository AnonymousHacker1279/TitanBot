import sqlite3


class StatisticsModule:

	def __init__(self, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
		self.connection = connection
		self.cursor = cursor

		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS command_usage_analytics (
				id INTEGER PRIMARY KEY,
					guild_id INTEGER,
					command_name TEXT CHECK( length(command_name) <= 255 ),
					module_name TEXT CHECK( length(module_name) <= 255 ),
					count INTEGER,
					UNIQUE(guild_id, command_name, module_name)
				)
		""")
		self.connection.commit()

	async def get_top_ten_commands(self, guild_id: int = None, get_global: bool = False) -> list:
		"""Get the top ten most used commands."""

		if get_global:
			# There may be multiple entries with the same command and module name in different guilds, so add them up
			self.cursor.execute("""
				SELECT command_name, module_name, SUM(count)
				FROM command_usage_analytics
				GROUP BY command_name, module_name
				ORDER BY SUM(count) DESC
				LIMIT 10
			""")
		else:
			self.cursor.execute("""
				SELECT command_name, module_name, count
				FROM command_usage_analytics
				WHERE guild_id = ?
				ORDER BY count DESC
				LIMIT 10
			""",
			(guild_id,))

		return self.cursor.fetchall()

	async def get_top_quoted_users(self, guild_id: int = None, get_global: bool = False) -> list:
		"""Get the top three most quoted users in a guild or globally, and the total number of their quotes."""

		if get_global:
			self.cursor.execute("""
				SELECT author, COUNT(author)
				FROM quotes
				GROUP BY author
				ORDER BY COUNT(author) DESC
				LIMIT 3
			""")
		else:
			self.cursor.execute("""
				SELECT author, COUNT(author)
				FROM quotes
				WHERE guild_id = ?
				GROUP BY author
				ORDER BY COUNT(author) DESC
				LIMIT 3
			""",
			(guild_id,))

		return self.cursor.fetchall()
