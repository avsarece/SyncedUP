"""Book Data"""
import streamlit as st
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_file = BASE_DIR / "data" / "allsonginfo.csv"
csv_file = str(csv_file)

st.set_page_config(page_title="Song Data", page_icon="🎶", layout="wide")
df = pd.read_csv(csv_file, dtype=str)

df_sorted = df.drop(columns=["lyrics", "id","song_id", "spotify_link"], errors="ignore")
st.title("Song Data")

st.write(df_sorted)
