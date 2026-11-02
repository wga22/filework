#!/bin/bash

#title          :updateplaylists
#description    :pull new versions of the playlists from Spiderman
#author         :will
#date           :20240415
#version        :1
#notes          : 
#bash_version   :5.2.15(1)-release
#============================================================================

set -e

SOURCE_SERVER="will@spiderman.local"
SOURCE_DIR="/media/ten/music/playlists/moode/"
TARGET_DIR="/var/lib/mpd/playlists/"
SSH_KEY="/home/will/.ssh/id_ecdsa"

# 1. Sync playlists (additive)
rsync -avz --inplace --progress \
  --include="*.m3u" \
  --exclude="*" \
  -e "ssh -i $SSH_KEY" \
  "$SOURCE_SERVER:$SOURCE_DIR" "$TARGET_DIR"

# 2. Clean carriage returns
sudo sed -i 's/\r$//' "$TARGET_DIR"*.m3u

# 3. Ensure #EXTIMG:local exists in each playlist header
for f in "$TARGET_DIR"*.m3u; do
    [ -e "$f" ] || continue
    if ! grep -q "^#EXTIMG:" "$f"; then
        sudo sed -i '1s/^/#EXTIMG:local\n/' "$f"
    fi
done

# 4. Set MPD permissions
sudo chown -R mpd:audio "$TARGET_DIR"
sudo chmod 664 "$TARGET_DIR"*.m3u

# 5. Extract missing artwork for any new playlists
sudo /usr/local/bin/gen_playlist_covers.sh

# 6. Inform MPD
mpc update >/dev/null 2>&1 || true

echo "Playlist sync and artwork verification complete."
