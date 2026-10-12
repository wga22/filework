import os
import re
from mutagen.easyid3 import EasyID3

# Directory containing your MP3s
MUSIC_DIR = "D:\\My Music\\Pop"  # Change this to your music directory



# Pattern matches (remix), (radio edit), (ft. ...), (remaster...), (live), etc.
NOISE_PATTERN = re.compile(
    r"\s*[\(\[]\s*.*?\b(remix|mix|radio edit|edit|single version|feat\.?|ft\.?|featuring|remaster(?:ed)?|live|acoustic)\b.*?[\)\]]",
    re.IGNORECASE,
)
changeCount=0
for root, _, files in os.walk(MUSIC_DIR):
    for file in files:
        if file.lower().endswith(".mp3"):
            path = os.path.join(root, file)
            try:
                audio = EasyID3(path)
                if "title" in audio:
                    original_title = audio["title"][0]
                    cleaned_title = NOISE_PATTERN.sub("", original_title).strip()
                    if cleaned_title != original_title:
                        print(f"'{original_title}' -> '{cleaned_title}'")
                        changeCount += 1
                        audio["title"] = cleaned_title
                        audio.save()
            except Exception as e:
                print(f"Error reading {file}: {e}")

print(f"Total titles changed: {changeCount}")