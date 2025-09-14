"""App interface
How to run: write streamlit run app_interface/app.py on terminal
"""
import streamlit as st
import pandas as pd
import backend.rec_system as rs
# from qdrant_client import QdrantClient
from pathlib import Path
import streamlit.components.v1 as components
from urllib.parse import urlparse


def run():
    iframe_src = "https://open.spotify.com/embed/track/59BweHnnNQc5Y55WO30JuK?utm_source=generator"
    components.iframe(iframe_src)


def spotify_to_embed(url: str) -> str:
    """
    Convert any Spotify share link into a valid embed URL.
    Works for track, album, playlist, artist, show, episode.
    """
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]

    # Handle localized URLs: /intl-xx/track/<id>
    if parts and parts[0].startswith("intl-"):
        parts = parts[1:]

    if len(parts) >= 2:
        kind, spotify_id = parts[0], parts[1]
        if kind in {"track", "album", "playlist", "artist", "show", "episode"}:
            return f"https://open.spotify.com/embed/{kind}/{spotify_id}"

    raise ValueError(f"Unrecognized Spotify URL: {url}")



# client = QdrantClient(host="localhost", port=6333)
st.set_page_config(page_title="Song Recommender", page_icon="🎶", layout="wide")

BASE_DIR = Path(__file__).resolve().parent.parent
csv_file = BASE_DIR / "data" / "allsonginfo.csv"
csv_file = str(csv_file)

df = pd.read_csv(csv_file)

songs = df["title"].astype(str)
artists = df["artist"].astype(str)
# album_cover_url = df['cover_url']
# song_url = df['url']
st.header('Song Recommender System')
selected_book = st.selectbox("Select a book:", (artists + ": " + songs).unique())

if st.button("Show Recommend"):
    _, song = selected_book.split(": ", 1)
    song1 = rs.query_to_qdrant(song, 3)[0]
    song2 = rs.query_to_qdrant(song, 3)[1]
    song3 = rs.query_to_qdrant(song, 3)[2]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"[**Title:** {song1['title']}]({song1['url']})")
        st.text(f"Artist: {song1['artist']}")
        st.text(f"Genre: {song1['genre']}")
        iframe_src = spotify_to_embed(song1['url'])
        components.iframe(iframe_src, height=152)
    with col2:
        st.markdown(f"[**Title:** {song2['title']}]({song2['url']})")
        st.text(f"Artist: {song2['artist']}")
        st.text(f"Genre: {song2['genre']}")
        iframe_src = spotify_to_embed(song2['url'])
        components.iframe(iframe_src, height=152)
    with col3:
        st.markdown(f"[**Title:** {song3['title']}]({song3['url']})")
        st.text(f"Artist: {song3['artist']}")
        st.text(f"Genre: {song3['genre']}")
        iframe_src = spotify_to_embed(song3['url'])
        components.iframe(iframe_src, height=152)
