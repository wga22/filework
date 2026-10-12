import json
import random
import re
import shutil
from datetime import datetime
from pathlib import Path, PurePosixPath

from plexapi.server import PlexServer

# Configuration
MUSIC_LIBRARY_NAME = "Music"
THUMBDRIVE_PATH = Path("e:/")
MUSIC_DIR = Path(r"D:\My Music\Pop")
PLEX_MUSIC_ROOT = PurePosixPath("/media/ten/music/Pop")
MAX_SONGS = 100
MIN_RATING = 6.0


def load_plex_credentials():
    credentials_path = Path(__file__).with_name("plex_credentials.json")
    with credentials_path.open(encoding="utf-8") as json_file:
        return json.load(json_file)


def selection_weight(track):
    rating = track.userRating
    stars = rating / 2.0
    weight = stars ** 2

    added_at = track.addedAt
    if added_at is not None:
        now = datetime.now(added_at.tzinfo)
        age_days = max((now - added_at).total_seconds() / 86400, 0)
        weight *= 1 + 1 / (1 + age_days / 365)

    return weight


def select_tracks(tracks, count):
    candidates = [
        track for track in tracks
        if track.userRating is not None and track.userRating >= MIN_RATING
    ]
    selected = []

    while candidates and len(selected) < count:
        chosen = random.choices(
            candidates,
            weights=[selection_weight(track) for track in candidates],
            k=1,
        )[0]
        selected.append(chosen)
        candidates.remove(chosen)

    return selected


def source_path_for(plex_path):
    direct_path = Path(plex_path)
    if direct_path.is_file():
        try:
            relative_path = direct_path.relative_to(MUSIC_DIR)
        except ValueError:
            return direct_path, None
        return direct_path, relative_path

    plex_path = PurePosixPath(plex_path)
    try:
        relative_path = plex_path.relative_to(PLEX_MUSIC_ROOT)
    except ValueError:
        return None, None

    source_path = MUSIC_DIR.joinpath(*relative_path.parts)
    return source_path, relative_path


def safe_folder_name(value):
    return re.sub(r'[<>:"/\\|?*]', "_", value).strip(" .") or "Unknown"


def copy_track(track):
    if not track.media or not track.media[0].parts:
        print(f"Skipping {track.title}: Plex has no file path")
        return False

    plex_path = track.media[0].parts[0].file
    source_path, relative_path = source_path_for(plex_path)
    if source_path is None or not source_path.is_file():
        print(f"Skipping {track.title}: source file not found for {plex_path}")
        return False

    if relative_path is None:
        artist = safe_folder_name(track.grandparentTitle or "Unknown Artist")
        album = safe_folder_name(track.parentTitle or "Unknown Album")
        relative_path = Path(artist) / album / source_path.name

    destination = THUMBDRIVE_PATH / Path(*relative_path.parts)
    if destination.exists():
        print(f"Skipping {track.title}: already on thumbdrive")
        return False

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
    except OSError as error:
        print(f"Could not copy {track.title}: {error}")
        return False

    print(f"Copied {track.grandparentTitle or 'Unknown Artist'} - {track.title}")
    return True

def main():
    plex_cred = load_plex_credentials()
    plex_url = plex_cred["baseurl"]
    plex_token = plex_cred["token"]
    print(f"Connecting to Plex at {plex_url}...")
    plex = PlexServer(plex_url, plex_token)
    music = plex.library.section(MUSIC_LIBRARY_NAME)
    tracks = music.search(libtype="track")
    selection = select_tracks(tracks, MAX_SONGS)

    print(f"Found {len(tracks)} tracks; selected {len(selection)} rated 3 stars or higher.")
    copied = sum(copy_track(track) for track in selection)
    print(f"Copied {copied} songs to {THUMBDRIVE_PATH}.")


if __name__ == "__main__":
    main()


