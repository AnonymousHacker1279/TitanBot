import lyricsgenius
import re

from Framework.GeneralUtilities import Constants

genius = lyricsgenius.Genius(Constants.GENIUS_API_TOKEN, verbose=False)


async def search_songs(artist: str, song: str):
	queryArtist = genius.search_artist(artist, max_songs=1, sort="title")
	if queryArtist is not None:
		querySong = queryArtist.song(song)
	else:
		return "No artist found."
	lyrics = querySong.lyrics
	# Do some cleanup, to get rid of random text at the end
	lyrics = re.sub('[0-9]+EmbedShare URLCopyEmbedCopy', "", lyrics)
	return lyrics, querySong.id


async def get_lyrics_by_url(url: str):
	lyrics = genius.lyrics(song_url=url)
	if lyrics is None:
		return "No lyrics found."
	# Do some cleanup, to get rid of random text at the end
	lyrics = re.sub('[0-9]+EmbedShare URLCopyEmbedCopy', "", lyrics)
	return lyrics


async def get_lyrics_by_id(songID: int):
	lyrics = genius.lyrics(song_id=songID)
	if lyrics is None:
		return "No lyrics found."
	# Do some cleanup, to get rid of random text at the end
	lyrics = re.sub('[0-9]+EmbedShare URLCopyEmbedCopy', "", lyrics)
	return lyrics
