import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="playlist-read-private playlist-read-collaborative"
)

sp = spotipy.Spotify(auth_manager=auth_manager)

def get_playlist_tracks(playlist_url):
        playlist_id = playlist_url.split("/")[-1].split("?")[0]
        """Fetches all track names and artists from a private Spotify playlist."""
        tracks = []
        test = sp.playlist(playlist_id)
        playlist_name = test['name']
        results = sp.playlist_tracks(playlist_id)
        while results:
            for j in results['items']:
                track = j['item']
                if track:
                    track_name = track['name']
                    artist_name = track['artists'][0]['name']
                    tracks.append({"track": track_name, "artist": artist_name})
            
            results = sp.next(results) if results['next'] else None
            
        print(f"Extracted {len(tracks)} tracks from Spotify playlist.")
        return tracks, playlist_name
