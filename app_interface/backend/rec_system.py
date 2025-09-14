"""Song Recommendation System"""
import pandas as pd
from sentence_transformers import SentenceTransformer
from torch import IntTensor
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Filter,
    FieldCondition,
    MatchValue
)
from pathlib import Path

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

client = QdrantClient(url="http://localhost:6333")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
csv_file = BASE_DIR / "data" / "allsonginfo.csv"  # Can change the csv_file path here
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


def genre_similarity(input_genre: str, genre2: str) -> float:
    """Calculate the similarity of input_genre and genre2"""
    embeddings1 = model.encode(input_genre.lower().strip())
    embeddings2 = model.encode(genre2.lower().strip())

    similarities = model.similarity(embeddings1, embeddings2)
    result = IntTensor.item(similarities)
    return result


def unweighted_similarity(input_song: str) -> list[dict[str, str | int | float]]:
    """Compute the unweighted similarity of the song with other songs in qdrant container
    Unweighted similarity only includes the lyrics embeddings.
    >>> unweighted_similarity("Viva La Vida")
    >>> unweighted_similarity("The Scientist")
    >>> unweighted_similarity("Yellow")
    """
    df = pd.read_csv(csv_file, header=0)

    input_id = song_to_id(input_song)
    song_row = df[df["id"] == input_id]
    lyrics = song_row["lyrics"].values[0]
    query_vec = model.encode([lyrics])[0].tolist()
    # quert_vec = transform_sentences()[1]

    hits = client.search(
        collection_name="song_db",
        query_vector=query_vec,
        query_filter=Filter(must_not=[FieldCondition(key="id", match=MatchValue(value=input_id))]),
        limit=1000,
        with_payload=['title', 'artist', 'genre'],
        with_vectors=False,
    )

    return [{**hit.payload, 'score': hit.score} for hit in hits]


def weighted_similarity(input_song: str, song2: str) -> float:
    """Compute the weighted similarity of two books, The weighted similarity includes:
    0.6 * text_embedding + 0.25 * genre_embedding + 0.15 * rating_embedding
    If the input_book does not exist... CONTINUE HERE
    >>> weighted_similarity("It's Only the Himalayas", "A Light in the Attic")
    >>> weighted_similarity("The Wedding Dress", 'Shopaholic Ties the Knot (Shopaholic #3)')
    """
    df = pd.read_csv(csv_file, header=0)

    input_id = song_to_id(input_song)
    input_row = df[df["id"] == input_id]

    match = next((x for x in unweighted_similarity(input_song) if
                  x['title'].strip().lower() == song2.strip().lower()), None)

    if match:
        text_sim = match['score']  # float
        song2_genre = match['genre']  # str

        input_genre = input_row["genre"].values[0]
        genre_sim = genre_similarity(input_genre, song2_genre)

        return 0.7 * text_sim + 0.3 * genre_sim

    else:
        print("Book not found.")


def find_most_similar(input_song: str) -> list:
    """Find the 3 books that are most similar to this book, using WEIGHTED similarity.
    >>> find_most_similar("Viva La Vida")
    >>> find_most_similar("Tipping the Velvet")
    >>> find_most_similar("How Music Works")
    >>> find_most_similar("The Most Perfect Thing: Inside (and Outside) a Bird's Egg")
    >>> find_most_similar("Something More Than This")
    >>> find_most_similar("The Wedding Dress")
    >>> find_most_similar("The 10% Entrepreneur: Live Your Startup Dream Without Quitting Your Day Job")
    """
    csv_path = csv_file
    df = pd.read_csv(csv_path, header=0)

    input_id = song_to_id(input_song)
    input_row = df[df["id"] == input_id]
    if input_row.empty:
        print(f"Song '{input_song}' not found in database.")
        return []

    lyrics = input_row["lyrics"].values[0]
    query_vec = model.encode([lyrics])[0].tolist()

    hits = client.search(
        collection_name="song_db",
        query_vector=query_vec,
        query_filter=Filter(must_not=[FieldCondition(key="id", match=MatchValue(value=input_id))]),
        limit=30,
        with_payload=['title', 'genre', 'artist'],
        with_vectors=False
        # score_threshold=0.4
    )

    scored_songs = []
    for hit in hits:
        similarity = weighted_similarity(input_song, hit.payload['title'])
        if similarity is not None:
            scored_songs.append({
                'title': hit.payload['title'],
                'artist': hit.payload['artist'],
                'genre': hit.payload['genre'],
                'score': similarity,
            })

    return sorted(scored_songs, key=lambda x: -x['score'])[:3]


def query_to_qdrant(song_name: str, k_final: int):
    """Send a query to qdrant, and print the closest 3 search results to this query.
    >>> query_to_qdrant('Creep', 4)
    >>> query_to_qdrant('Slide', 4)
    >>> query_to_qdrant('Fix You')
    >>> query_to_qdrant('Scar Tissue')
    >>> query_to_qdrant("Viva La Vida")
    """
    df = pd.read_csv(csv_file, header=0)
    input_id = song_to_id(song_name)
    song_row = df[df["id"] == input_id]
    song_lyrics = song_row['lyrics'].values[0]
    song_genre = song_row['genre'].values[0]
    song_artist = song_row['artist'].values[0]

    embedding = model.encode(song_lyrics)
    client = QdrantClient("localhost", port=6333)
    search_result = client.search(
        collection_name="song_db",
        query_vector=embedding,
        query_filter=Filter(must_not=[FieldCondition(key="id", match=MatchValue(value=input_id)),
                                      FieldCondition(key="artist", match=MatchValue(value=song_artist))]),
        with_payload=True,
        score_threshold=0.4,
        limit=50
    )

    rescored = []
    for h in search_result:
        vec_score = h.score
        g_score = genre_similarity(song_genre, h.payload['genre'])
        blended = 0.7 * vec_score + 0.3 * g_score
        rescored.append({**h.payload, 'vec_score': vec_score, 'score': blended})

    return sorted(rescored, key=lambda x: x['score'], reverse=True)[:k_final]

    # scored_songs = [
        # {**hit.payload, 'score': 0.7 * hit.score + 0.3 * genre_similarity(song_genre, hit.payload['genre'])}
        # for hit in search_result
    # ]
