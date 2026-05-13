"""App interface
How to run: write streamlit run app_interface/app.py on terminal
"""
import streamlit as st
import pandas as pd
import backend.rec_system as rs
from pathlib import Path
from urllib.parse import urlparse


def spotify_to_embed(url: str) -> str:
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]

    if parts and parts[0].startswith("intl-"):
        parts = parts[1:]

    if len(parts) >= 2:
        kind, spotify_id = parts[0], parts[1]
        if kind in {"track", "album", "playlist", "artist", "show", "episode"}:
            return f"https://open.spotify.com/embed/{kind}/{spotify_id}"

    raise ValueError(f"Unrecognized Spotify URL: {url}")


def spotify_embed(url: str, height: int = 352) -> None:
    embed_url = spotify_to_embed(url)
    st.markdown(
        f'<iframe src="{embed_url}" width="100%" height="{height}" '
        f'frameborder="0" allow="autoplay; clipboard-write; encrypted-media; '
        f'fullscreen; picture-in-picture" loading="lazy"></iframe>',
        unsafe_allow_html=True
    )


st.set_page_config(page_title="Song Recommender", page_icon="🎶", layout="wide")

BASE_DIR = Path(__file__).resolve().parent.parent
csv_file = BASE_DIR / "data" / "allsonginfo.csv"

df = pd.read_csv(str(csv_file))

songs = df["title"].astype(str)
artists = df["artist"].astype(str)

st.header('SyncedUP')
selected_book = st.selectbox("Select a song:", (artists + ": " + songs).unique())

if st.button("Show Recommend"):
    _, song = selected_book.split(": ", 1)
    results = rs.query_to_qdrant(song, 3)

    col1, col2, col3 = st.columns(3)

    for col, song_data in zip([col1, col2, col3], results):
        with col:
            st.markdown(f"[**Title:** {song_data['title']}]({song_data['url']})")
            st.text(f"Artist: {song_data['artist']}")
            st.text(f"Genre: {song_data['genre']}")
            spotify_embed(song_data['url'])
