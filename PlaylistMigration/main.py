import src.spotify_extractor as spotify
import src.youtube_loader as youtube

def main():
    # 1. Inputs
    SPOTIFY_PLAYLIST_ID = "https://open.spotify.com/playlist/6Wm8mBviAKq66GHlSNXSSt?si=2fb048299d6949ab"
    
    print("--- Starting Playlist Migration Pipeline ---")
    
    # 2. Extract from Spotify
    tracks, YOUTUBE_PLAYLIST_TITLE = spotify.get_playlist_tracks(SPOTIFY_PLAYLIST_ID)
    
    if not tracks:
        print("No tracks found or authentication failed.")
        return

    # 3. Load/Push to YouTube
    yt_playlist_id = youtube.create_playlist(
        title=YOUTUBE_PLAYLIST_TITLE, 
        description="Migrated automatically from Spotify via Python pipeline."
    )
    
    print(f"Transferring {len(tracks)} tracks to YouTube...")
    for item in tracks:
        youtube.search_and_add_track(yt_playlist_id, item["track"], item["artist"])
        
    print("--- Pipeline Execution Complete! ---")

if __name__ == "__main__":
    main()