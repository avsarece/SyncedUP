import http.client
import json
import ssl
import certifi
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os
import time

BASE_DIR = Path(__file__).resolve().parent
csv_file = BASE_DIR / "data" / "songdatafull_final.csv"
csv_file = str(csv_file)

load_dotenv()
access_token = os.getenv("ACCESS_TOKEN1")

df = pd.read_csv(csv_file)
song_titles = df['title'].astype(str).fillna('')
song_artists = df['artist'].astype(str).fillna('')

results = {'song_details': []}
# Use certifi's trusted CA bundle
context = ssl.create_default_context(cafile=certifi.where())
for idx, (song_title, song_artist) in enumerate(zip(song_titles, song_artists), 1):
    conn = http.client.HTTPSConnection("google.serper.dev", context=context)
    payload = json.dumps({"q": song_artist + ' ' + song_title}).encode("utf-8")
    headers = {
        'X-API-KEY': access_token,
        'Content-Type': 'application/json'
    }
    try:

        conn.request("POST", "/search", body=payload, headers=headers)
        res = conn.getresponse()
        data = res.read()
        print("# "+ str(idx) + " "+f"Results for '{song_title}' from '{song_artist}':")
        print(data.decode("utf-8"))

        response_data = json.loads(data.decode("utf-8"))
        organic_lst = response_data.get("organic", [])
        knowledgeGraph = response_data.get("knowledgeGraph", {})
        spotify_link = []

        for i, item1 in enumerate(organic_lst, 1):

            if 'https://open.spotify.com/' in item1.get('link', '').lower():
                spotify_link.append({
                    "song_link": item1.get('link'),
                })
                break
        # album_url = knowledgeGraph.get('imageUrl')
        result = {
            "song_id": idx,
            "song_title": song_title,
            "song_artist": song_artist,
            "spotify_link": spotify_link,
            # "album_url": album_url
        }
        results['song_details'].append(result)

        with open('url_scraping1.json', 'w', encoding='utf-8') as outfile:
            json.dump(results, outfile, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Error processing '{song_title}': {str(e)}")
    finally:
        conn.close()

    time.sleep(1.5)

# album_url = knowledgeGraph.get('imageUrl')
