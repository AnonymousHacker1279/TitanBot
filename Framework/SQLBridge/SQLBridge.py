import os
import sqlite3

from Framework.SQLBridge.CFModule import CFModule
from Framework.SQLBridge.QuotesModule import QuotesModule
from Framework.SQLBridge.StatisticsModule import StatisticsModule


class SQLBridge:

	def __init__(self):
		if sqlite3.threadsafety == 3:
			check_same_thread = False
		else:
			check_same_thread = True
		self.connection = sqlite3.connect(f"{os.getcwd()}/Storage/TitanBot.db", check_same_thread=check_same_thread)
		self.cursor = self.connection.cursor()

		self.cf_module = CFModule(self.connection, self.cursor)
		self.quotes_module = QuotesModule(self.connection, self.cursor)
		self.statistics_module = StatisticsModule(self.connection, self.cursor)

		self.cursor.execute("""
			CREATE TABLE IF NOT EXISTS bot_logs (
				id INTEGER PRIMARY KEY,
					source TEXT CHECK( length(source) <= 255 ),
					log_level TEXT CHECK( log_level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') ),
					message TEXT,
					timestamp TIMESTAMP
				)
		""")

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

	async def write_log_entry(self, source: str, level: str, message: str, timestamp: str) -> None:
		"""Write a log entry into the `bot_logs` table."""

		# Remove any newlines at the end of the message
		message = message.rstrip("\n")

		self.cursor.execute("""
			INSERT INTO bot_logs (source, log_level, message, timestamp)
			VALUES (?, ?, ?, ?)
		""",
		(source, level, message, timestamp))

		self.connection.commit()

	async def update_command_used(self, guild_id: int, command_name: str, module_name: str):
		"""Update the analytics for the number of times a command has been used."""

		self.cursor.execute("""
			INSERT INTO command_usage_analytics (guild_id, command_name, module_name, count)
			VALUES (?, ?, ?, 1)
			ON CONFLICT(guild_id, command_name, module_name)
			DO UPDATE SET count = count + 1
		""",
		(guild_id, command_name, module_name))

		self.connection.commit()
