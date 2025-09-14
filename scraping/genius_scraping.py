"""Scarping"""
import lyricsgenius
import pandas as pd
import json
from pathlib import Path
from dotenv import load_dotenv
import os
import time


BASE_DIR = Path(__file__).resolve().parent.parent
artists_csv = BASE_DIR / "data" / "artists.csv"
artists_csv = str(artists_csv)

BASE_DIR = Path(__file__).resolve().parent.parent
songs_json = BASE_DIR / "data" / "songdatafull_final.json"
songs_json = str(songs_json)

load_dotenv()
access_token = os.getenv("ACCESS_TOKEN")
LyricsGenius = lyricsgenius.Genius(access_token, timeout=30)

df = pd.read_csv(artists_csv)
artists = df['artist_name']  # When Genius gives timeout error, continue from where it left off by adding .iloc[index:]
genres = df['artist_genre']


def artist_to_genre(input_artist: str):
    """Return the genre of the input_artist.
    >>> artist_to_genre('Maroon 5')
    """
    df = pd.read_csv(artists_csv, header=0)

    genre = (
        df.loc[df["artist_name"] == input_artist, "artist_genre"]
        .fillna("")
        .values[0]
        .strip()
        .lower()
    )

    return genre.lower()


def scraping():
    data = {'song_details': []}
    count = 0
    for artist in artists:
        artistx = LyricsGenius.search_artist(artist, 5)
        if artistx is None:  # Skip if artist not found
            print(f"Artist not found: {artist}")
            continue
        songs = artistx.songs
        for song in songs:
            data['song_details'].append({'title': song.title,
                                         'artist': artist,
                                         'lyrics': song.lyrics,
                                         'genre': artist_to_genre(artist)
                                         })
            count += 1

        with open('songdata7.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print('# of songs scraped:', count)
        time.sleep(1)
