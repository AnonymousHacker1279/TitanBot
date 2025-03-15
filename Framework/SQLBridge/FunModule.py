import sqlite3


class FunModule:

	def __init__(self, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
		self.connection = connection
		self.cursor = cursor

		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS stab_analytics (
				id INTEGER PRIMARY KEY,
				guild_id INTEGER,
				author_id INTEGER,
				times_stabbed INTEGER DEFAULT 0,
				times_stabbed_others INTEGER DEFAULT 0,
				UNIQUE(guild_id, author_id)
			)
		""")
		self.connection.commit()

	async def update_user_stabbed(self, guild_id: int, author_id: int, inverse: bool = False):
		"""
		Update the analytics for the number of times a user has been stabbed, or stabbed others.

		:param guild_id: The ID of the guild.
		:param author_id: The ID of the author.
		:param inverse: Set that user has stabbed someone else, rather than been stabbed.
		"""

		if inverse:
			self.cursor.execute("""
				INSERT INTO stab_analytics (guild_id, author_id, times_stabbed_others)
				VALUES (?, ?, 1)
				ON CONFLICT(guild_id, author_id)
				DO UPDATE SET times_stabbed_others = times_stabbed_others + 1
			""",
(guild_id, author_id))
		else:
			self.cursor.execute("""
				INSERT INTO stab_analytics (guild_id, author_id, times_stabbed)
				VALUES (?, ?, 1)
				ON CONFLICT(guild_id, author_id)
				DO UPDATE SET times_stabbed = times_stabbed + 1
			""",
(guild_id, author_id))

		self.connection.commit()
