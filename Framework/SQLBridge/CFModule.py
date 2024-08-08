import sqlite3


class CFModule:

	def __init__(self, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
		self.connection = connection
		self.cursor = cursor

	async def add_project(self, guild_id: int, project_id: int, announcement_channel_id: int, latest_file_id: int) -> bool:
		"""Add a CF project to the update checker."""

		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS cf_projects (
				id INTEGER PRIMARY KEY,
					guild_id INTEGER,
					project_id INTEGER,
					announcement_channel_id INTEGER,
					latest_file_id INTEGER
				)
		""")

		# Do not add if an entry already exists
		self.cursor.execute("""
			SELECT 1
			FROM cf_projects
			WHERE guild_id = ? AND project_id = ?
		""",
		(guild_id, project_id))

		if self.cursor.fetchone() is None:
			self.cursor.execute("""
				INSERT INTO cf_projects (guild_id, project_id, announcement_channel_id, latest_file_id)
				VALUES (?, ?, ?, ?)
			""",
			(guild_id, project_id, announcement_channel_id, latest_file_id))

			self.connection.commit()
			return True
		else:
			return False

	async def remove_project(self, guild_id: int, project_id: int):
		"""Remove a CF project from the update checker."""

		self.cursor.execute("""
			DELETE FROM cf_projects
			WHERE guild_id = ? AND project_id = ?
		""",
		(guild_id, project_id))

		self.connection.commit()

	async def get_projects(self, guild_id: int = -1) -> list:
		"""Get all CF projects in a guild being checked for updates."""

		if guild_id == -1:
			self.cursor.execute("""
				SELECT project_id, announcement_channel_id, latest_file_id
				FROM cf_projects
			""")
		else:
			self.cursor.execute("""
				SELECT project_id, announcement_channel_id, latest_file_id
				FROM cf_projects
				WHERE guild_id = ?
			""",
			(guild_id,))

		return self.cursor.fetchall()

	async def update_project_version(self, project_id: int, latest_file_id: int):
		"""Update the version of a CF project."""

		self.cursor.execute("""
			UPDATE cf_projects
			SET latest_file_id = ?
			WHERE project_id = ?
		""",
		(latest_file_id, project_id))

		self.connection.commit()
