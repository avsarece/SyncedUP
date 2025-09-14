import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# Client Credentials Flow (works for some endpoints)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-library-read",  # Adjust scopes as needed
))

# Now try fetching audio features
features = sp.audio_features(["70LcF31zb1H0PyJoS1Sx1r"])
print(features)
