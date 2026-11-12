#!/usr/bin/env bash
set -e

SOURCE_SERVER="will@spiderman.local"
REMOTE_BACKUP_DIR="/media/ten/music/playlists/moode/backups"
SSH_KEY="/home/will/.ssh/id_ecdsa"
LOCAL_INCOMING_DIR="/var/local/incoming_backups"
TIMESTAMP_FILE="/var/local/incoming_backups/backup_import.timestamp"

mkdir -p "$LOCAL_INCOMING_DIR"

# 1. Initialize timestamp file if missing
if [ ! -f "$TIMESTAMP_FILE" ]; then
    touch -t 197001010000 "$TIMESTAMP_FILE"
fi

# 2. Query remote server for the newest .zip file in the backup directory
# ls -t sorts by modification time descending; head -n 1 grabs the newest
NEWEST_REMOTE_FILE=$(ssh -i "$SSH_KEY" "$SOURCE_SERVER" \
    "ls -t $REMOTE_BACKUP_DIR/*.zip 2>/dev/null | head -n 1" || true)

if [ -z "$NEWEST_REMOTE_FILE" ]; then
    echo "$(date): No .zip backup files found on $SOURCE_SERVER:$REMOTE_BACKUP_DIR"
    exit 0
fi

REMOTE_FILENAME=$(basename "$NEWEST_REMOTE_FILE")
LOCAL_TARGET_ZIP="$LOCAL_INCOMING_DIR/$REMOTE_FILENAME"

# 3. Pull the newest file while preserving modification timestamps (-p)
scp -p -i "$SSH_KEY" "$SOURCE_SERVER:$NEWEST_REMOTE_FILE" "$LOCAL_TARGET_ZIP"
chmod 644 "$LOCAL_TARGET_ZIP"

# 4. Compare timestamps: check if the downloaded zip is newer than TIMESTAMP_FILE
if [ "$LOCAL_TARGET_ZIP" -nt "$TIMESTAMP_FILE" ]; then
    echo "$(date): New backup detected ($REMOTE_FILENAME). Starting import..."

    # 5. Invoke moOde's station manager import utility
    if sudo python3 /var/www/util/station_manager.py --import "$LOCAL_TARGET_ZIP"; then
        echo "$(date): Station import succeeded."

        # Update timestamp file to match the backup's modification time
        touch -r "$LOCAL_TARGET_ZIP" "$TIMESTAMP_FILE"

        # 6. Clear radio cover URL cache and reload worker/web services
        php -r 'require_once "/var/www/inc/common.php"; require_once "/var/www/inc/radio.php"; clearRadioCoverUrlCache();' 2>/dev/null || true
        sudo moodeutl -r

        echo "$(date): Radio stations and caches successfully refreshed."
    else
        echo "$(date): Error: station_manager.py import failed for $LOCAL_TARGET_ZIP" >&2
        exit 1
    fi
else
    echo "$(date): $REMOTE_FILENAME has already been imported or is not newer than last run."
fi
