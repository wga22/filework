'''
2025-04 - modified to account for "song.delete" was not working to just delete the file directly from the OS
'''

import json
import os
import platform
from plexapi.server import PlexServer
import plexapi.exceptions

# Check if running on Windows
if platform.system() == "Windows":
    print("Error: This script cannot be run on Windows. Please run it on the Linux Plex server.")
    exit(1)

# Load Plex credentials
with open('plex_credentials.json') as json_file:
    plex_cred = json.load(json_file)

# Connect to Plex server
try:
    plex = PlexServer(plex_cred['baseurl'], plex_cred['token'])
except Exception as e:
    print(f"Failed to connect to Plex server: {e}")
    exit(1)

# Find and process BAD_MUSIC playlist
for playlist in plex.playlists():
    if playlist.title == "BAD_MUSIC":
        print(f"Removing all songs from: {playlist.title}")
        for song in playlist.items():
            if song.TYPE != 'track':
                print(f"Skipping {song.title}: Not a track (Type: {song.TYPE})")
                continue
            file_path = song.media[0].parts[0].file if song.media and song.media[0].parts else "Unknown"
            print(f"{song.artist().title} - {song.title} - Key: {song.key} - File: {file_path}")
            try:
                song.reload()  # Ensure metadata is valid
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)  # Delete file directly
                    print(f"Manually deleted file: {file_path}")
                song.delete()  # Remove metadata
                print(f"Deleted metadata for {song.title}")
            except plexapi.exceptions.BadRequest as e:
                print(f"Failed to delete metadata for {song.title}: {e}")
                print("Running library scan to remove orphaned metadata")
                plex.library.section('Music').update()  # Scan to remove orphaned metadata
            except OSError as e:
                print(f"Failed to delete file {file_path}: {e}")
            except Exception as e:
                print(f"Unexpected error for {song.title}: {e}")
        break
else:
    print("Playlist 'BAD_MUSIC' not found.")