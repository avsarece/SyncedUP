"""Data organizing/creating"""
import pandas as pd
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
artists_csv = BASE_DIR / "artists.csv"
artists_csv = str(artists_csv)


def merge_json_files(file_paths, output_file):
    """
    Merge json files in a single file.
    >>> merge_json_files(['songdata1.json','songdata2.json','songdata3.json'],'songdatafull.json')
    """
    BASE_DIR = Path(__file__).resolve().parent
    data_dir = BASE_DIR  # input folder
    output_path = BASE_DIR / output_file

    merged_data = []
    for filename in file_paths:
        file_path = data_dir / filename
        with open(file_path, 'r') as file:
            data = json.load(file)
            merged_data.extend(data['song_details'])
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump({'song_details': merged_data}, outfile, indent=4, ensure_ascii=False)


def merge_csv(file_paths, output_file):
    """Merge csv files based on id"""

    dfs = [pd.read_csv(file) for file in file_paths]
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = pd.merge(merged_df, df, on='id', how='outer')
    merged_df.to_csv(output_file, index=False)


def remove_more(description: str) -> str:
    """Remove the background info about the song lyrics."""
    markers = ("… Read More", "... Read More")
    for m in markers:
        idx = description.find(m)  # returns -1 if not found (no exception)
        if idx != -1:
            cut = idx + len(m)
            # strip regular spaces, tabs, newlines, and NBSP right after the marker
            return description[cut:].lstrip(" \t\r\n\u00A0")
    return description  # marker not present; return as-is


def create_table(filename: str, output_file: str) -> None:
    """create_table('songdatafull.json','songdatafull.csv')
    """
    BASE_DIR = Path(__file__).resolve().parent
    json_path = BASE_DIR / filename

    with open(json_path, encoding='utf-8') as jf:
        d = json.load(jf)

    songs = d['song_details']
    for song in songs:
        song['lyrics'] = remove_more(song['lyrics'])

    for idx, song in enumerate(songs, start=1):
        song['id'] = idx

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        cw = csv.writer(f)
        header = list(songs[0].keys())  # Convert to list so we can modify it
        # Optional: move 'id' to the first column
        header.remove('id')
        header.insert(0, 'id')
        cw.writerow(header)

        for song in songs:
            row = [song[col] for col in header]  # Ensure correct order
            cw.writerow(row)


def remove_link_extras(filename: str):
    """Remove the link extras from url scraping"""
    df = pd.read_csv(filename)
    df['spotify_link'] = df['spotify_link'].str.extract(r"'song_link': '([^']+)'")
    df.to_csv('cleaned_file.csv', index=False)


def drop_na(filename: str, output_file: str):
    """Drop all the NA issued columns in the csv file and create a new clean csv_file"""
    df = pd.read_csv(filename)
    df1 = df.dropna()
    df1.to_csv(output_file, index=False)


def artist_to_genre(input_artist: str) -> str:
    """Return the genre of the input_artist.
    >>> artist_to_genre('Maroon 5')
    >>> 'pop'
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


def get_info(filename: str):
    """Get how many artists and songs are in filename
    >>> get_info('allsonginfo.csv')
    # of songs: 960
    # of artists: 202
    """
    BASE_DIR = Path(__file__).resolve().parent
    songinfo_csv = BASE_DIR / filename
    df = pd.read_csv(songinfo_csv)
    songs = len(df)
    artists = len(df.groupby('artist'))
    print('# of songs: ' + str(songs))
    print('# of artists: ' + str(artists))

# BASE_DIR = Path(__file__).resolve().parent
# data = BASE_DIR / "data" / 'uptodate.csv'  # input folder
# df = pd.read_csv(data)
# artist_genre_map = {}
# for artist in df['artist'].unique():  # Process each artist only once
# artist_genre_map[artist] = artist_to_genre(artist)

# df['genre'] = df['artist'].map(artist_genre_map)
# df.to_csv('OUTPUTALLCORRECT.csv', index=False)
