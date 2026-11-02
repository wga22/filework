#!/usr/bin/python3
#
# moOde audio player (C) 2014 Tim Curtis
# http://moodeaudio.org

import drivers
import subprocess
import random
import sys
from datetime import datetime
import time

display = drivers.Lcd()

# fixed fields
nowstr = time.strftime('%a %I:%M')
hostname = "http://basement.lan/"

# Load the values from the currentsong file
songattr = {}
try:
    with open("/var/local/www/currentsong.txt") as file1:
        for line in file1:
            if "=" in line:
                name, var = line.partition("=")[::2]
                songattr[name.strip()] = var.strip()
except FileNotFoundError:
    sys.exit(1)

# --- Logic Updates ---

# 1) Display "album" if "artist" equals "Radio station"
artist_display = songattr.get("artist", "")
if artist_display.lower() == "radio station":
    artist_display = songattr.get("album", "Radio Station")

# 2) Clean up title if longer than 45 characters
title_display = songattr.get("title", "")
if len(title_display) > 45:
    # Pull characters up to the first "-"
    title_display = title_display.split('-')[0].strip()

# --- Display Output ---

display.lcd_display_string(artist_display, 1)
display.lcd_display_string(title_display, 2)
display.lcd_display_string(nowstr, 3)
display.lcd_display_string(hostname, 4)

