import re
from typing import Optional

import lyricsgenius

from Framework.ConfigurationManager import ConfigurationValues


async def cleanup(lyrics) -> str:
	"""Clean up the lyrics to remove unnecessary text."""
	if lyrics is None:
		return "No lyrics found."

	lyrics = re.sub(r'[0-9]+EmbedShare URLCopyEmbedCopy', "", lyrics)
	lyrics = re.sub(r'[0-9]+Embed', "", lyrics)
	lyrics = re.sub(r'Embed', "", lyrics)
	lyrics = re.sub(r'You might also like', "", lyrics)
	lyrics = re.sub(r'(.*) (LiveGet tickets as low as \$)(\d*)', "", lyrics)

	# Remove the first line, which is the song title
	lyrics = lyrics.splitlines(True)[1:]
	lyrics = ''.join(lyrics)

	return lyrics


class GeniusAPI:

	def __init__(self):
		self.genius: Optional[lyricsgenius.Genius] = None

	async def initialize(self) -> None:
		"""Initialize the Genius API."""
		self.genius = lyricsgenius.Genius(ConfigurationValues.GENIUS_API_TOKEN, verbose=False)

	async def search_songs(self, artist: str, song: str) -> tuple[str, int]:
		"""Search for a song by an artist."""
		artist = self.genius.search_artist(artist, max_songs=1, sort="title")
		song = artist.song(song)

		lyrics = song.lyrics
		lyrics = await cleanup(lyrics)

		return lyrics, song.id

	async def get_lyrics_by_url(self, url: str) -> str:
		"""Get lyrics by URL."""
		return await cleanup(self.genius.lyrics(song_url=url))

	async def get_lyrics_by_id(self, song_id: int) -> str:
		"""Get lyrics by ID."""
		return await cleanup(self.genius.lyrics(song_id=song_id))
