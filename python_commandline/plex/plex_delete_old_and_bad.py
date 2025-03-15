#!/usr/bin/env python3
from plexapi.server import PlexServer
import os
import sys
import time

# Plex server connection details (replace with your values)
PLEX_URL = "http://your.plex.server.ip:32400"
PLEX_TOKEN = "your_plex_token"

# Target directory to search within (this is now a starting point)
TARGET_DIR = "/path/to/subfolder"

# Number of days for the age check
DAYS_OLD = 400

def get_plex_files(target_dir):
    """Finds all files in Plex libraries that are within the target directory or its subdirectories."""
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        plex_files = []

        for section in plex.library.sections():
            if section.location.startswith(target_dir) or target_dir.startswith(section.location): # Check if the directory is within the library location
                for item in section.all(): # Iterate through all items in the library
                    if item.userRating == 1: # Check if the item has 1 star rating
                        if item.media[0].parts[0].file.startswith(target_dir): # Only add files that are in the target directory or its subdirectories
                            plex_files.append(item.media[0].parts[0].file)
        return plex_files

    except Exception as e:
        print(f"Plex connection or other error: {e}", file=sys.stderr)
        return []


def is_file_old(filepath, days=DAYS_OLD):
    """Checks if a file is older than the specified number of days."""
    try:
        file_stats = os.stat(filepath)
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        return file_stats.st_mtime < cutoff_time
    except OSError as e:
        print(f"Error checking file age for {filepath}: {e}", file=sys.stderr)
        return False


def delete_file(filepath):
    """Deletes the given file."""
    try:
        os.remove(filepath)
        print(f"Deleted: {filepath}")
    except OSError as e:
        print(f"Error deleting {filepath}: {e}", file=sys.stderr)
        return False

def modify_timestamp(filepath):
    """Modifies the timestamp of the file to the current time."""
    try:
        now = time.time()
        os.utime(filepath, (now, now))
        print(f"Modified timestamp: {filepath}")
    except OSError as e:
        print(f"Error modifying timestamp of {filepath}: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    plex_files = get_plex_files(TARGET_DIR)

    for filepath in plex_files:
        if is_file_old(filepath):
            modify_timestamp(filepath)
            if delete_file(filepath):
                continue
            else:
                print(f"Failed to delete {filepath}", file=sys.stderr)
        else:
            print(f"File {filepath} is a 1-star rating but not older than {DAYS_OLD} days. Skipping.")