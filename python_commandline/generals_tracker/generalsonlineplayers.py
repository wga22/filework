import json
import re
import requests
import psycopg
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Configuration
PLAYERS_URL = "https://www.playgenerals.online/players"
TIMEOUT = 10  # seconds
CONFIG_PATH = Path(__file__).with_name("generals_dev_spec.json")

def parse_duration_to_minutes(duration_str):
    """
    Parses duration strings like '2H', '3M', '33S', or '1H 15M 30S'
    and converts them into total minutes (including decimal representation for seconds).
    """
    if not duration_str:
        return 0.0

    duration_str = str(duration_str).upper().strip()

    # Match numbers before D, H, M, and S
    days = re.search(r'(\d+)\s*D', duration_str)
    hours = re.search(r'(\d+)\s*H', duration_str)
    minutes = re.search(r'(\d+)\s*M', duration_str)
    seconds = re.search(r'(\d+)\s*S', duration_str)

    total_minutes = 0.0

    if days:
        total_minutes += float(days.group(1)) * 24 * 60
    if hours:
        total_minutes += float(hours.group(1)) * 60
    if minutes:
        total_minutes += float(minutes.group(1))
    if seconds:
        total_minutes += float(seconds.group(1)) / 60.0

    # Fallback if no letter units were present (e.g., colon format HH:MM:SS)
    if not (days or hours or minutes or seconds):
        parts = duration_str.split(':')
        try:
            if len(parts) == 3:  # HH:MM:SS
                total_minutes = float(parts[0]) * 60 + float(parts[1]) + float(parts[2]) / 60.0
            elif len(parts) == 2:  # MM:SS
                total_minutes = float(parts[0]) + float(parts[1]) / 60.0
            else:
                total_minutes = float(duration_str)
        except ValueError:
            total_minutes = 0.0

    return round(total_minutes, 2)

def fetch_and_parse_players():
    """Fetch players page HTML and parse lobby/game statuses and durations dynamically."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(PLAYERS_URL, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    player_data = []

    # Select table rows
    rows = soup.select("table.players-table tr, .player-row, tr.player")
    if not rows:
        rows = soup.find_all("tr")[1:]

    for row in rows:
        cols = row.find_all(["td", "th"])
        if len(cols) < 2:
            continue

        name = cols[0].get_text(strip=True)
        name = name.removeprefix("Player name")
        
        raw_status = ""
        raw_duration = ""

        # Scan through all columns in the row dynamically to extract status and duration
        for col in cols[1:]:
            cell_text = col.get_text(strip=True)

            # Check if cell matches duration patterns (contains digit + H/M/S or HH:MM)
            if re.search(r'\d+\s*[HMS]', cell_text, re.IGNORECASE) or re.search(r'^\d+:\d+', cell_text):
                raw_duration = cell_text
            # Identify status cell (ignoring client strings)
            elif any(kw in cell_text.lower() for kw in ["game", "lobby", "playing", "staging", "idle"]):
                if "client" not in cell_text.lower():
                    raw_status = cell_text

        # Standardize status
        if "game" in raw_status.lower() or "playing" in raw_status.lower():
            status = "game"
        elif "lobby" in raw_status.lower() or "staging" in raw_status.lower() or "idle" in raw_status.lower():
            status = "lobby"
        else:
            #status = raw_status if raw_status else "unknown"
            status = raw_status

        duration_mins = parse_duration_to_minutes(raw_duration)

        player_data.append({
            "name": name,
            "status": status,
            "duration": duration_mins
        })

    return player_data

def load_config():
    """Load application settings and accept either Players key casing."""
    with CONFIG_PATH.open(encoding="utf-8") as config_file:
        config = json.load(config_file)

    players_key = next(
        (key for key in config if key.casefold() == "players"), None
    )
    if players_key is None or not isinstance(config[players_key], dict):
        raise ValueError("Config must contain a Players object.")
    return config, config[players_key]

def get_postgres_connection(config):
    """Create a PostgreSQL connection from the JSON postgres settings."""
    postgres_config = config.get("postgres")
    if not isinstance(postgres_config, dict):
        raise ValueError("Config must contain a postgres object.")

    return psycopg.connect(
        host=postgres_config["host"],
        port=postgres_config.get("port", 5432),
        dbname=postgres_config["database"],
        user=postgres_config["username"],
        password=postgres_config["password"],
    )

def ensure_database_schema(cursor):
    """Create the users and sessions tables if they do not already exist."""
    schema_path = Path(__file__).with_name("generals_schema.sql")
    cursor.execute(schema_path.read_text(encoding="utf-8"), prepare=False)

def sync_users(cursor, configured_users):
    """Upsert every configured owner/handle pair into users."""
    for user_name, handles in configured_users.items():
        if isinstance(handles, str):
            handles = [handles]
        if not isinstance(handles, list):
            raise ValueError(f"Handles for {user_name!r} must be a list.")

        for handle in handles:
            handle = str(handle).strip()
            if not handle:
                continue
            cursor.execute(
                """
                INSERT INTO tesla.users (user_name, handle)
                VALUES (%s, %s)
                ON CONFLICT (user_name, handle)
                DO NOTHING
                """,
                (str(user_name), handle),
            )

def record_player_sessions(players):
    """Synchronize configured users and persist their online sessions."""
    config, configured_users = load_config()
    players_by_handle = {
        player["name"].strip().casefold(): player
        for player in players
        if player.get("name", "").strip()
    }

    with get_postgres_connection(config) as connection:
        with connection.cursor() as cursor:
            ensure_database_schema(cursor)
            sync_users(cursor, configured_users)

            cursor.execute(
                """
                SELECT row_id, handle, last_seen
                FROM tesla.users
                ORDER BY row_id
                """
            )
            users = cursor.fetchall()
            cursor.execute(
                """
                SELECT row_id, user_row_id, duration_mins
                FROM tesla.sessions
                WHERE end_time IS NULL
                """
            )
            open_sessions = {
                user_row_id: (session_id, float(duration))
                for session_id, user_row_id, duration in cursor.fetchall()
            }
            cursor.execute("SELECT CURRENT_TIMESTAMP")
            checked_at = cursor.fetchone()[0]
            matched_players = {}

            for user_row_id, handle, last_seen in users:
                player = players_by_handle.get(handle.strip().casefold())
                active_session = open_sessions.get(user_row_id)

                if player is None:
                    if active_session is not None:
                        session_id, _ = active_session
                        cursor.execute(
                            """
                            UPDATE tesla.sessions
                            SET end_time = COALESCE(%s, %s)
                            WHERE row_id = %s AND end_time IS NULL
                            """,
                            (last_seen, checked_at, session_id),
                        )
                    continue

                observed_duration = float(player.get("duration", 0.0))
                matched_players.setdefault(handle.strip().casefold(), player)
                if active_session is None:
                    cursor.execute(
                        """
                        INSERT INTO tesla.sessions (user_row_id, start_time, duration_mins)
                        VALUES (%s, %s, %s)
                        """,
                        (
                            user_row_id,
                            checked_at - timedelta(minutes=observed_duration),
                            observed_duration,
                        ),
                    )
                else:
                    session_id, stored_duration = active_session
                    elapsed_minutes = 0.0
                    if last_seen is not None:
                        elapsed_minutes = max(
                            0.0, (checked_at - last_seen).total_seconds() / 60.0
                        )
                    updated_duration = max(
                        stored_duration + elapsed_minutes, observed_duration
                    )
                    cursor.execute(
                        """
                        UPDATE tesla.sessions
                        SET duration_mins = %s
                        WHERE row_id = %s AND end_time IS NULL
                        """,
                        (updated_duration, session_id),
                    )

                cursor.execute(
                    "UPDATE tesla.users SET last_seen = %s WHERE row_id = %s",
                    (checked_at, user_row_id),
                )
    return list(matched_players.values())

def display_players(players):
    """Print the list of active players in standard format."""
    print(f"\n{'Player Name':<25} | {'Status':<8} | {'Duration (mins)':<15}")
    print("-" * 55)
    
    if not players:
        print("No players found in lobby or game.")
        return

    for p in players:
        print(f"{p['name']:<25} | {p['status']:<8} | {p['duration']:<15.2f}")
        
    print(f"\nTotal Players Tracked: {len(players)}")

def main():
    """Single execution run to fetch and display player statuses."""
    print(f"\n=== Generals Online Player Status [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ===")
    try:
        players = fetch_and_parse_players()
        matched_players = record_player_sessions(players)
        display_players(matched_players)
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
    except Exception as e:
        print(f"Parsing error: {e}")

if __name__ == "__main__":
    main()