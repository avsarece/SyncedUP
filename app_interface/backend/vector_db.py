"""Create a song db and upload it to qdrant"""
from sentence_transformers import SentenceTransformer
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from qdrant_client.http.models import PointStruct
import nltk
from pathlib import Path
from torch import IntTensor
import streamlit as st


TOKENIZER = nltk.data.load('tokenizers/punkt/english.pickle')

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

qdrant_client = QdrantClient(
    url=st.secrets["QDRANT_URL"],
    api_key=st.secrets["QDRANT_API_KEY"]
)
qdrant_client.recreate_collection(
    collection_name="song_db",
    vectors_config=VectorParams(size=384, distance=Distance.DOT),
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_file = BASE_DIR / "data" / "allsonginfo.csv"
csv_file = str(csv_file)


def song_to_id(input_song: str) -> str:
    """Create a dictionary that maps every song title to its corresponding id,
    and return the id of the book.
        >>> song_to_id("Viva La Vida")

    """
    csv_path = csv_file
    df = pd.read_csv(csv_path, header=0)
    ids = df["id"].fillna("").astype(int)

    dictionary = {}
    for id in ids:
        title = (
            df.loc[df["id"] == id, "title"]
            .fillna("")
            .values[0]
            .strip()
            .lower()
        )
        dictionary[title] = id

    input_song_lower = input_song.strip().lower()
    return dictionary[input_song_lower]


def split_sentences(description: str) -> list:
    """Split the sentences, store them in a list and remove the '...more'
    """

    if description == '':
        return ['']

    list1 = TOKENIZER.tokenize(description)
    list1.pop()
    return list1


def transform_sentences(batch_size: int = 64):
    """Transform the book description using SentenceTransformer and upsert to Qdrant"""
    csv_path = csv_file
    df = pd.read_csv(csv_path, header=0)
    lyrics = df["lyrics"].fillna("").astype(str)
    genres = df["genre"].fillna("").astype(str)
    ids = df["id"].fillna(0).astype(int)
    titles = df['title'].fillna("").astype(str)
    artists = df['artist'].fillna("").astype(str)
    urls = df['spotify_link'].fillna("").astype(str)

    lyrics_list = []
    song_details = []  # tuple containing book info

    for lyric, id, genre, title, artist, url in zip(lyrics, ids, genres, titles, artists, urls):
        song_details.append((lyric, genre, id, title, artist, url))
        lyrics_list.append(lyric)

    embeddings = model.encode(
        lyrics_list,
        batch_size=batch_size,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    lyrics_result = [pair[0] for pair in song_details]
    genres_result = [pair[1] for pair in song_details]
    ids_result = [pair[2] for pair in song_details]
    titles_result = [pair[3] for pair in song_details]
    artists_result = [pair[4] for pair in song_details]
    urls_result = [pair[5] for pair in song_details]

    return lyrics_result, embeddings, ids_result, genres_result, titles_result, artists_result, urls_result


def upload_to_qdrant(lyrics, embeddings, ids, genres, titles, artists,urls, batch_size=100):
    """Uploads sentence embeddings with associated metadata to a Qdrant vector database."""

    points = []
    for idx, (lyric, vector, id, genre, title, artist, url) in enumerate(
            zip(lyrics, embeddings, ids, genres, titles, artists, urls), start=1):
        points.append(PointStruct(
            id=idx,
            vector=vector.tolist(),
            payload={
                "id": int(id),
                "title": title,
                "artist": artist,
                "genre": genre,
                "lyrics": lyric,
                "url": url

            }
        ))

        if len(points) >= batch_size:
            qdrant_client.upsert(collection_name="song_db", wait=True, points=points)
            points = []

    if points:
        qdrant_client.upsert(collection_name="song_db", wait=True, points=points)


lyrics, embeddings, ids, genres, titles, artists, urls = transform_sentences()
upload_to_qdrant(lyrics, embeddings, ids, genres, titles, artists, urls)

# Retract first 15 data from collection
points, next_page = qdrant_client.scroll(
    collection_name="song_db",
    limit=15,
    with_payload=True,  # Also include other metadata
    with_vectors=True,
)

# Print the points
for point in points:
    print(f"ID: {point.id}")
    print(f"Title     : {point.payload.get('title')}")
    print(f"Genre: {point.payload.get('genre')}")
    print(f"Description: {point.payload.get('lyrics')[:10]}")
    print(f"Vector  : {point.vector[:5]} ...")
    print("---")


def genre_similarity(input_genre: str, genre2: str) -> float:
    """Calculate the similarity of input_genre and genre2"""
    embeddings1 = model.encode(input_genre.lower().strip())
    embeddings2 = model.encode(genre2.lower().strip())

    similarities = model.similarity(embeddings1, embeddings2)
    result = IntTensor.item(similarities)
    return result
