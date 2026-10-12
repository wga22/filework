import re
import glob
import hashlib
import os
import shutil
import logging
import email
import mimetypes
import unicodedata
#from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import json

# Configuration
PLEX_URL = "http://127.0.0.1:32400"
PLEX_TOKEN = "YOUR_PLEX_TOKEN_HERE"
MUSIC_LIBRARY_NAME = "Music"

with open('./plex/plex_credentials.json') as json_file:
    plex_cred = json.load(json_file)
    PLEX_URL = plex_cred['baseurl']
    PLEX_TOKEN = plex_cred['token']

def normalize(text):
    """Normalize string for fuzzy comparison (lowercase, strip accents/symbols)."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    return "".join(c for c in text.lower() if c.isalnum() or c.isspace()).strip()

def set_play_count(track, play_count):
    current_count = track.viewCount or 0
    if current_count == play_count:
        return

    track.markUnplayed()
    for _ in range(play_count):
        track.markPlayed()

def main():
    print(f"Connecting to Plex at {PLEX_URL}...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    music = plex.library.section(MUSIC_LIBRARY_NAME)

    print("Fetching all tracks from Plex (this may take a minute for large libraries)...")
    tracks = music.searchTracks()

    # Step 1: Map all tracks that have an existing rating
    rated_map = {}
    for track in tracks:
        # Plex ratings are floats: 2.0 = 1 star, 4.0 = 2 stars, ..., 10.0 = 5 stars
        if track.userRating is not None and track.userRating > 0:
            artist_name = normalize(track.grandparentTitle)
            title = normalize(track.title)
            key = (artist_name, title)
            
            # Keep the highest rating if duplicate records exist
            if key not in rated_map or track.userRating > rated_map[key].userRating:
                rated_map[key] = track

    print(f"Found {len(rated_map)} distinct rated (Artist, Title) combinations.")

    # Step 2: Find unrated tracks and copy the matching rating over
    updated_count = 0
    skipped_count = 0

    for track in tracks:
        # Check for unrated tracks
        if track.userRating is None or track.userRating == 0:
            artist_name = normalize(track.grandparentTitle)
            title = normalize(track.title)
            key = (artist_name, title)

            if key in rated_map:
                source_track = rated_map[key]
                target_rating = source_track.userRating
                source_play_count = source_track.viewCount or 0
                #print(f"[MATCH] Rating '{track.grandparentTitle} - {track.title}' -> {target_rating / 2.0:.1f} stars")
                #print(f"[PLAY COUNT] '{track.grandparentTitle} - {track.title}' -> {source_play_count}")
                set_play_count(track, source_play_count)
                track.rate(target_rating)
                updated_count += 1
            else:
                print(f"[NO-MATCH] Rating '{track.grandparentTitle} - {track.title}")
                skipped_count += 1

    print("\n--- Summary ---")
    print(f"Successfully rated: {updated_count} tracks")
    print(f"Unmatched / still unrated: {skipped_count} tracks")

if __name__ == "__main__":
    main()


