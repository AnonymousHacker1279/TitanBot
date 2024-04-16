import re
from typing import Optional

import lyricsgenius

from Framework.ConfigurationManager import ConfigurationValues


class GeniusAPI:

	def __init__(self):
		self.genius: Optional[lyricsgenius.Genius] = None

	async def initialize(self) -> None:
		self.genius = lyricsgenius.Genius(ConfigurationValues.GENIUS_API_TOKEN, verbose=False)

	async def search_songs(self, artist: str, song: str) -> tuple[str, int]:
		artist = self.genius.search_artist(artist, max_songs=1, sort="title")
		song = artist.song(song)

		lyrics = song.lyrics
		lyrics = await self.__cleanup_lyrics(lyrics)

		return lyrics, song.id

	async def get_lyrics_by_url(self, url: str) -> str:
		return await self.__get_lyrics(self.genius.lyrics(song_url=url))

	async def get_lyrics_by_id(self, song_id: int) -> str:
		return await self.__get_lyrics(self.genius.lyrics(song_id=song_id))

	async def __get_lyrics(self, lyrics) -> str:
		if lyrics is None:
			return "No lyrics found."

		return await self.__cleanup_lyrics(lyrics)

	async def __cleanup_lyrics(self, lyrics):
		# Do some cleanup, to get rid of random text at the end
		lyrics = re.sub(r'[0-9]+EmbedShare URLCopyEmbedCopy', "", lyrics)
		lyrics = re.sub(r'[0-9]+Embed', "", lyrics)
		lyrics = re.sub(r'Embed', "", lyrics)
		lyrics = re.sub(r'You might also like', "", lyrics)
		lyrics = re.sub(r'(.*) (LiveGet tickets as low as \$)(\d*)', "", lyrics)

		# Remove the first line, which is the song title
		lyrics = lyrics.splitlines(True)[1:]
		lyrics = ''.join(lyrics)

		return lyrics
