import sqlite3

import discord


class QuotesModule:

	def __init__(self, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
		self.connection = connection
		self.cursor = cursor

		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS quotes (
				id INTEGER PRIMARY KEY,
					guild_id INTEGER,
					quote_number INTEGER,
					content TEXT,
					author INTEGER,
					quoted_by INTEGER,
					date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				)
		""")

		self.connection.commit()

	async def add_quote(self, guild_id: int, content: str, author: int, quoted_by: int) -> int:
		"""Add a quote to the database."""

		# Get the next quote number
		next_quote_number = 0
		self.cursor.execute("""
			SELECT MAX(quote_number)
			FROM quotes
			WHERE guild_id = ?
		""",
		(guild_id,))
		row = self.cursor.fetchone()
		if row[0] is not None:
			next_quote_number = row[0] + 1

		# Add the quote
		self.cursor.execute("""
			INSERT INTO quotes (guild_id, quote_number, content, author, quoted_by)
			VALUES (?, ?, ?, ?, ?)
		""",
		(guild_id, next_quote_number, content, author, quoted_by))

		self.connection.commit()
		return next_quote_number

	async def remove_quote(self, guild_id: int, quote_number: int) -> bool:
		"""Remove a quote from the database."""

		# Check if the given quote number exists
		self.cursor.execute("""
			SELECT 1
			FROM quotes
			WHERE guild_id = ? AND quote_number = ?
		""",
		(guild_id, quote_number))
		if self.cursor.fetchone() is None:
			return False
		else:
			self.cursor.execute("""
				DELETE FROM quotes
				WHERE guild_id = ? AND quote_number = ?
			""",
			(guild_id, quote_number))

			# Update the quote numbers
			self.cursor.execute("""
				SELECT quote_number
				FROM quotes
				WHERE guild_id = ?
				ORDER BY quote_number
			""",
			(guild_id,))
			quotes = self.cursor.fetchall()
			for i, quote in enumerate(quotes):
				self.cursor.execute("""
					UPDATE quotes
					SET quote_number = ?
					WHERE guild_id = ? AND quote_number = ?
				""",
				(i, guild_id, quote[0]))

			self.connection.commit()
			return True

	async def edit_quote(self, guild_id: int, quote_id: int, quote: str = None, author: discord.User = None) -> bool:
		"""Edit a quote in the database."""

		# Check if the given quote number exists
		self.cursor.execute("""
			SELECT 1
			FROM quotes
			WHERE guild_id = ? AND quote_number = ?
		""",
		(guild_id, quote_id))
		if self.cursor.fetchone() is None:
			return False
		else:
			if quote is not None:
				self.cursor.execute("""
					UPDATE quotes
					SET content = ?
					WHERE guild_id = ? AND quote_number = ?
				""",
				(quote, guild_id, quote_id))
			if author is not None:
				author_id = author.id
				self.cursor.execute("""
					UPDATE quotes
					SET author = ?
					WHERE guild_id = ? AND quote_number = ?
				""",
				(author_id, guild_id, quote_id))
			self.connection.commit()
			return True

	async def get_quote(self, guild_id: int, quote_id: int = None) -> list:
		"""Get a quote from the database. If no quote ID is provided, a random quote will be returned."""

		if quote_id is not None:
			self.cursor.execute("""
				SELECT quote_number, content, author, quoted_by, date_added
				FROM quotes
				WHERE guild_id = ? AND quote_number = ?
				limit 1
			""",
			(guild_id, quote_id))
			return self.cursor.fetchone()
		else:
			self.cursor.execute("""
				SELECT quote_number, content, author, quoted_by, date_added
				FROM quotes
				WHERE guild_id = ?
				ORDER BY RANDOM()
				limit 1
			""",
			(guild_id,))
			return self.cursor.fetchone()

	async def get_total_quotes(self, guild_id: int, get_global_count: bool = False) -> int:
		"""Get the total number of quotes in the database."""

		if get_global_count:
			self.cursor.execute("""
				SELECT COUNT(*)
				FROM quotes
			""")
		else:
			self.cursor.execute("""
				SELECT COUNT(*)
				FROM quotes
				WHERE guild_id = ?
			""",
			(guild_id,))
		return self.cursor.fetchone()[0]

	async def search_by_author(self, guild_id: int, author_id: int, page: int = 0, descending_order: bool = False) -> tuple[list, int]:
		"""Search for quotes by a specific author. Paginates the results with 10 per page."""

		ordering = "ASC"
		if descending_order:
			ordering = "DESC"

		self.cursor.execute(f"""
			SELECT quote_number, content, author, quoted_by, date_added
			FROM quotes
			WHERE guild_id = ? AND author = ?
			ORDER BY quote_number {ordering}
			LIMIT 10 OFFSET ?
		""",
		(guild_id, author_id, page * 10))
		# Return the list of quotes and the total number of quotes for the author
		quotes = self.cursor.fetchall()
		self.cursor.execute("""
			SELECT COUNT(*)
			FROM quotes
			WHERE guild_id = ? AND author = ?
		""",
		(guild_id, author_id))

		total = self.cursor.fetchone()
		if total is not None:
			total = total[0]
		else:
			total = 0

		return quotes, total

	async def search_by_text(self, guild_id: int, search_term: str, page: int = 0, descending_order: bool = False) -> tuple[list, int]:
		"""Search for quotes by a specific author. Paginates the results with 10 per page."""

		ordering = "ASC"
		if descending_order:
			ordering = "DESC"

		search_term = f"%{search_term}%"

		self.cursor.execute(f"""
			SELECT quote_number, content, author, quoted_by, date_added
			FROM quotes
			WHERE guild_id = ? AND content LIKE ?
			ORDER BY quote_number {ordering}
			LIMIT 10 OFFSET ?
		""",
		(guild_id, search_term, page * 10))
		# Return the list of quotes and the total number of quotes for the author
		quotes = self.cursor.fetchall()
		self.cursor.execute("""
			SELECT COUNT(*)
			FROM quotes
			WHERE guild_id = ? AND content LIKE ?
		""",
		(guild_id, search_term))

		total = self.cursor.fetchone()
		if total is not None:
			total = total[0]
		else:
			total = 0

		return quotes, total

	async def list_recent(self, guild_id: int) -> list:
		"""List the most recent quotes added to the database."""

		self.cursor.execute("""
			SELECT quote_number, content, author, quoted_by, date_added
			FROM quotes
			WHERE guild_id = ?
			ORDER BY date_added DESC
			LIMIT 10
		""",
		(guild_id,))
		return self.cursor.fetchall()
