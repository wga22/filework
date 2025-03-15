#!/usr/bin/env python
from gmusicapi import Mobileclient
import sys
import time
import re

### Functions
def downRateSong(dupeSong):
	dupeSong.rating = '1'
	api.change_song_metadata(dupeSong)


def fixthumbs():
	songLists = api.get_all_songs(True, False)
	uniqueSongs = {}
	thumbsDownSongs = {}
	counter = 0
	for songs in songLists:
		for song in songs:
			title = re.sub("^the ", "", song['title'].lower())
			title = re.sub("\W", "", title)
			artist = re.sub("\W", "", song['artist']).lower()
			key = artist +"-"+ title
			#print "Song: " + title + " - " + artist
			#if key in uniqueSongs and song['rating'] != '1' and song['deleted'] == False:
			if key in uniqueSongs:
				#print "Dupe found:" + key
				if key in thumbsDownSongs:
					print key + " is good"
					thumbsDownSongs[key]["safe"] = 1
			else:
				uniqueSongs[key] = song
				if song.get('rating','0') == '1':
					thumbsDownSongs[key] = song
					
	for tdSong in thumbsDownSongs:
		print tdSong
		break
		#if tdSong["safe"] != 1:
		#	print tdSong["title"]
	#for x in thumbsDownSongs:
	#	print "nice: "  + x["id"]
	#api.rate_songs(thumbsDownSongs, '1')
	print "found " + str(len(thumbsDownSongs)) + " songs that shouldnt be thumbs down"
		
		
		#tracks = playlist['tracks']
		#find_and_remove_dups(api, tracks)

# Display help and exit if arguments present			
if len(sys.argv) != 1:
	print "USAGE:"
	print "./delete_dups_from_playlists.py"
	print
	print "	 Will delete all duplicate songs within each playlist" 
	exit(0)

# Setup the gmusicapi
api = Mobileclient()
api.__init__()


# Check to see if OAuth credentials available, ask user to setup if not
try:
	api.oauth_login(Mobileclient.FROM_MAC_ADDRESS)
	#api.perform_oauth()
except:
	print "No OAuth credentials found! Please setup in the following screen!"
	api.perform_oauth()
	api.oauth_login(Mobileclient.FROM_MAC_ADDRESS) # If it fails here, it wasn't meant to be

# Then, move on to doing all the work
if api.is_authenticated():
	print "Successfully logged in. Finding duplicates in playlists"
	fixthumbs()
	api.logout()
else:
	print "Not logged in! Exiting..."
	exit(1)

print "Script has finished successfully!"

