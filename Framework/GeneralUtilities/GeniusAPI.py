from typing import Optional

import lyricsgenius
import requests
from lyricsgenius.types import Artist, Song

from Framework.ConfigurationManager import ConfigurationManager


class GeniusAPI:

	def __init__(self):
		self.genius: Optional[lyricsgenius.Genius] = None

	async def initialize(self, configuration_manager: ConfigurationManager) -> None:
		"""Initialize the Genius API."""
		try:
			self.genius = lyricsgenius.Genius(await configuration_manager.get_value("genius/genius_api_key"), verbose=False, skip_non_songs=False)
		except TypeError:
			self.genius = None

	async def search_songs(self, a: str, s: str) -> tuple[str, int]:
		"""Search for a song by an artist."""
		artist: Artist = self.genius.search_artist(a, max_songs=1, sort="title")

		if artist is None:
			return "Unable to find artist information.", 0

		song: Song = artist.song(s)

		if song is None:
			return "Unable to find song information.", 0

		if song.lyrics == "":
			return "This song is an instrumental.", song.id

		return song.lyrics, song.id

	async def get_lyrics_by_id(self, song_id: int) -> tuple[str, str]:
		"""Get lyrics by ID."""
		if song_id == 0:
			return "", "Invalid song ID."

		try:
			song: Song = self.genius.song(song_id=song_id)
		except requests.HTTPError:
			return "", "Failed to retrieve song information."

		if song.lyrics is None:
			return "", "Unable to find song information."

		if song.lyrics == "":
			return "", "This song is an instrumental."

		return f"{song.artist} - {song.title}", song.lyrics
