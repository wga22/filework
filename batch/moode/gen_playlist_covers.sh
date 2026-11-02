#!/usr/bin/env bash
set -e

COVERS_DIR="/var/local/www/imagesw/playlist-covers"
PLAYLIST_DIR="/var/lib/mpd/playlists"
MUSIC_ROOT="/var/lib/mpd/music"

mkdir -p "$COVERS_DIR"

for m3u in "$PLAYLIST_DIR"/*.m3u; do
    [ -e "$m3u" ] || continue
    
    pl_name="$(basename "$m3u" .m3u)"
    target_img="$COVERS_DIR/${pl_name}.jpg"

    # Only process if cover does not already exist
    if [ ! -f "$target_img" ]; then
        # Collect all non-comment, non-empty tracks from the playlist
        tracks=()
        while IFS= read -r line; do
            line="$(echo "$line" | tr -d '\r')"
            [[ -z "$line" || "$line" =~ ^# ]] && continue
            
            # Resolve relative MPD path
            if [[ "$line" != /* ]]; then
                full_path="$MUSIC_ROOT/$line"
            else
                full_path="$line"
            fi
            
            [ -f "$full_path" ] && tracks+=("$full_path")
        done < "$m3u"

        track_count=${#tracks[@]}
        if [ "$track_count" -gt 0 ]; then
            # Pick a random track index
            rand_idx=$((RANDOM % track_count))
            selected_track="${tracks[$rand_idx]}"
            echo "${selected_track} ${pl_name}"
            # Extract embedded image using ffmpeg
            if ffmpeg -v error -y -i "$selected_track" -an -vcodec copy "$target_img" 2>/dev/null; then
                # Ensure it's scaled to a clean thumbnail size matching moOde standards
                ffmpeg -v error -y -i "$target_img" -vf "scale=300:300:force_original_aspect_ratio=decrease" "/tmp/${pl_name}_tmp.jpg" 2>/dev/null && mv "/tmp/${pl_name}_tmp.jpg" "$target_img"
                echo "Generated cover for $pl_name from $(basename "$selected_track")"
            else
                rm -f "$target_img"
            fi
        fi
    fi
done

sudo chown -R www-data:www-data "$COVERS_DIR"
sudo chmod 644 "$COVERS_DIR"/*.jpg 2>/dev/null || true
