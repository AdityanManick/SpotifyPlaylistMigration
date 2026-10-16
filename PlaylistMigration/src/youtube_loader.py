import os
from dotenv import load_dotenv
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

# Disable OAuthlib's HTTPS verification when running locally
load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_config = {
    "installed": {
        "client_id": os.getenv("YOUTUBE_CLIENT_ID"),
        "client_secret": os.getenv("YOUTUBE_CLIENT_SECRET"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(client_config, scopes)
#client_secrets_file = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secret.json")
credentials = flow.run_local_server(port=8080)

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

def create_playlist(title: str, description: str = ""):
        """Creates a new YouTube playlist and returns its ID."""
        request = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["Migration", "SpotifyTransfer"],
                    "defaultLanguage": "en"
                },
                "status": {
                    "privacyStatus": "public"
                }
            }
        )
        response = request.execute()
        playlist_id = response["id"]
        print(f"Created YouTube Playlist: {title} (ID: {playlist_id})")
        return playlist_id

def search_and_add_track(playlist_id: str, track_name: str, artist_name: str):
        """Searches for a track on YouTube and adds the first result to the playlist."""
        query = f"{track_name} {artist_name} audio"
        try:
            search_request = youtube.search().list(
                part="snippet",
                maxResults=1,
                q=query,
                type="video"
            )
            search_response = search_request.execute()
            
            if search_response["items"]:
                video_id = search_response["items"][0]["id"]["videoId"]
                
                # Add video to playlist
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {
                                "kind": "youtube#video",
                                "videoId": video_id
                            }
                        }
                    }
                ).execute()
                print(f"Added to YouTube: {track_name} - {artist_name}")
            else:
                print(f"Track not found on YouTube: {track_name} - {artist_name}")
                
        except googleapiclient.errors.HttpError as e:
            print(f"An HTTP error occurred: {e}")