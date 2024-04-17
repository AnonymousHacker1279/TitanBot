import re

from rich.highlighter import Highlighter


class TBHighlighter(Highlighter):
	"""A highlighter for anything sent over IPC."""

	def __init__(self):
		self.style = "white"
		self.color_of_next_entry = None

	def highlight(self, text):
		lines = text.plain.splitlines()
		current_position = 0
		specific_highlights = []

		# Process each line individually
		for line in lines:
			# Calculate the start and end positions of the line in the original text
			start = current_position
			end = start + len(line)

			log_level_regex = r"/([A-Z]+)\]:"
			log_level = re.search(log_level_regex, line)

			if log_level:
				text.stylize(self.style_log(log_level), start=start, end=end)
			elif self.color_of_next_entry:
				text.stylize(self.color_of_next_entry)
			else:
				text.stylize("white")

			# Check for color tags in the line
			sections = re.split(r'(\[color=[^\]]*\].*?\[/color\])', line)

			# Process each section
			for section in sections:
				# Check if the section starts with a color tag
				if section.startswith('[color='):
					# Extract the color from the tag
					color = re.search(r'\[color=([^\]]*)\]', section).group(1)

					# Remove the color tag from the section
					section_without_tags = re.sub(r'\[color=[^\]]*\](.*)\[/color\]', r'\1', section)

					# Calculate the start and end indexes after removing the color tags
					start = text.plain.find(section)
					end = start + len(section_without_tags)

					# Replace the section with the section without tags in text.plain
					text.plain = text.plain.replace(section, section_without_tags)

					# Add the section without tags and its style to the highlights dictionary
					specific_highlights.append((section_without_tags, color, start, end))
				else:
					# Update the start position to the end of the section
					start += len(section)

			# Update the current position to the end of the line plus one for the newline character
			current_position = end + 1

		# Apply the highlights to the text
		for highlight, color, start, end in specific_highlights:
			text.stylize(color, start=start, end=end)

		self.color_of_next_entry = None

	def style_log(self, log_level: re.Match[str]) -> str:
		log_level = log_level.group(1)
		style = ""

		match log_level:
			case "DEBUG":
				style = "bright_cyan"
			case "INFO":
				style = "bright_green"
			case "WARNING":
				style = "bright_yellow"
			case "ERROR":
				style = "bright_red"
			case "CRITICAL":
				style = "bright_magenta"

		return style
