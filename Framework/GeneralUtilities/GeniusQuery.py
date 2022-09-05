import re

import lyricsgenius

from Framework.GeneralUtilities import Constants

genius = lyricsgenius.Genius(Constants.GENIUS_API_TOKEN, verbose=False)


async def search_songs(artist: str, song: str):
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
	lyrics = re.sub('[0-9]+EmbedShare URLCopyEmbedCopy', "", lyrics)
	lyrics = re.sub('[0-9]+Embed', "", lyrics)
	lyrics = re.sub('Embed', "", lyrics)

	# Remove the first line, which is the song title
	lyrics = lyrics.splitlines(True)[1:]
	lyrics = ''.join(lyrics)

	return lyrics
