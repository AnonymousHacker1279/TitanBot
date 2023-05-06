import re

import lyricsgenius

from Framework.FileSystemAPI.ConfigurationManager import ConfigurationValues

genius = None
is_initialized = False


async def initialize():
	global genius
	genius = lyricsgenius.Genius(ConfigurationValues.GENIUS_API_TOKEN, verbose=False)
	global is_initialized
	is_initialized = True


async def search_songs(artist: str, song: str):
	if not is_initialized:
		await initialize()

	queryArtist = genius.search_artist(artist, max_songs=1, sort="title")
	if queryArtist is not None:
		querySong = queryArtist.song(song)
	else:
		return "No artist found."
	lyrics = querySong.lyrics
	lyrics = await __cleanup_lyrics(lyrics)
	return lyrics, querySong.id


async def get_lyrics_by_url(url: str):
	lyrics = genius.lyrics(song_url=url)
	return __get_lyrics(lyrics)


async def get_lyrics_by_id(songID: int):
	lyrics = genius.lyrics(song_id=songID)
	return __get_lyrics(lyrics)


async def __get_lyrics(lyrics):
	if lyrics is None:
		return "No lyrics found."
	lyrics = await __cleanup_lyrics(lyrics)
	return lyrics


async def __cleanup_lyrics(lyrics):
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
