client_config = {
    "installed": {
        "client_id": gclientid,
        "client_secret": gsecret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["https://127.0.0.1:8080"]
    }
}

# Define scope required to manage YouTube playlists
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Run OAuth Flow (similar to Spotify, it will prompt you to authorize via a link if token isn't cached)
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_config(client_config, scopes)
flow.redirect_uri = "https://localhost:8080"
# Note: For Databricks notebooks, you can generate credentials locally or use flow.run_console()
auth_uri, _ = flow.authorization_url(prompt="consent")
print(f"Please navigate to the following URL: {auth_uri}")
print("After authenticating, copy the authorization code and paste it below:")
code = input("Enter the authorization code: ")
flow.fetch_token(authorization_response=code)

credentials = flow.credentials

# Build the YouTube API client
youtube = build("youtube", "v3", credentials=credentials)

playlist_request = youtube.playlists().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "Migrated Fav Playlist",
            "description": "Migrated automatically via Databricks and PySpark ETL pipeline",
            "tags": ["databricks", "etl", "migration"]
        },
        "status": {
            "privacyStatus": "public" # Can be 'public', 'private', or 'unlisted'
        }
    }
)
playlist_response = playlist_request.execute()
target_playlist_id = playlist_response["id"]
print(f"Created YouTube Playlist ID: {target_playlist_id}")

def search_youtube_video(track_name, artist_name):
    query = f"{track_name} {artist_name} audio"
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=1
    )
    response = request.execute()
    if response['items']:
        return response['items'][0]['id']['videoId']
    return None


cleaned_tracks = spark.table('playlist_migration.playlist_tracks').collect()

for row in cleaned_tracks:
    video_id = search_youtube_video(row['track_name'], row['artist_name'])
    
    if video_id:
        # Add video to the newly created playlist
        add_request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": target_playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        )
        add_request.execute()
        print(f"Added to YouTube Music: {row['track_name']} by {row['artist_name']}")

print("Playlist migration to YouTube Music completed successfully!")