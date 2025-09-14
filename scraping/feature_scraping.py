"""Song feature scraping"""
import pandas as pd
import json
from pathlib import Path
from urllib.parse import urlparse
from requests import post
import os
import base64
import requests
from dotenv import load_dotenv



BASE_DIR = Path(__file__).resolve().parent.parent
song_csv = BASE_DIR / "data" / "allsonginfo.csv"
song_csv = str(song_csv)

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")

    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result =json.loads(result.content)
    token = json_result["access_token"]
    return token

token = get_token()
track_id = "1QFh8OH1e78dGd3VyJZCAC"  # from Spotify API examples

url1 = f"https://api.spotify.com/v1/tracks/{track_id}"
url2 = f"https://api.spotify.com/v1/audio-analysis/{track_id}"

print(requests.get(url1, headers={"Authorization": f"Bearer {token}"}).json())
print(requests.get(url2, headers={"Authorization": f"Bearer {token}"}).json())


def song_to_url(song: str):
    """Given the song name, return its url link
    >>> song_to_url('Creep')
    """
    df = pd.read_csv(song_csv, header=0)

    link = (
        df.loc[df["song_title"] == song, "spotify_link"]
        .fillna("")
        .values[0]
        .strip()

    )

    return link


def song_to_id(song: str) -> str:
    """
    Get the track id of the song
    >>> song_to_id('Creep')
    """
    url = song_to_url(song)
    if url.startswith("spotify:track:"):
        return url.split(":")[-1]
    parsed = urlparse(url)
    parts = parsed.path.split("/")
    if "track" in parts:
        return parts[parts.index("track") + 1].split("?")[0]

    raise ValueError(f"Could not extract track ID from {url}")
