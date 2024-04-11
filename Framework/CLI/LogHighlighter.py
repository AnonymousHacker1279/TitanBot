import re

from rich.highlighter import Highlighter


class LogHighlighter(Highlighter):
	"""A highlighter for log messages."""

	def __init__(self):
		self.style = "white"

	def highlight(self, text):
		# Split the text into lines
		lines = text.plain.splitlines()

		# Regex to get the log level
		level_regex = r"/([A-Z]+)\]:"

		# Initialize the current position
		current_position = 0

		# Process each line individually
		for line in lines:
			# Calculate the start and end positions of the line in the original text
			start = current_position
			end = start + len(line)

			log_level = re.search(level_regex, line)

			if log_level:
				log_level = log_level.group(1)

				match log_level:
					case "DEBUG":
						self.style = "bright_cyan"
					case "INFO":
						self.style = "bright_green"
					case "WARNING":
						self.style = "bright_yellow"
					case "ERROR":
						self.style = "bright_red"
					case "CRITICAL":
						self.style = "bright_magenta"

			# Apply the style to the line
			text.stylize(self.style, start=start, end=end)

			# Update the current position to the end of the line plus one for the newline character
			current_position = end + 1
