#!/usr/bin/env python
from gmusicapi import Mobileclient
import sys
import time
import re

#  2019-05 - working well, 
#
#


### Functions
def downRateSong(dupeSong):
	dupeSong.rating = '1'
	api.change_song_metadata(dupeSong)

def stripString(str, removeThe):
	str = str.lower()
	if removeThe:
		str = re.sub("^the ", "", str)
	artist = re.sub("\W", "", str)
	return str

def dedupeSongs():
	songLists = api.get_all_songs(True, False)
	uniqueSongs = {}
	thumbsDownSongs = []
	counter = 0
	for songs in songLists:
		for song in songs:
			title = stripString(song['title'], False)
			artist = stripString(song['artist'], True)
			key = artist +"-"+ title
			#print "Song: " + title + " - " + artist
			#if key in uniqueSongs and song['rating'] != '1' and song['deleted'] == False:
			#if song.get('rating', "5") != '1':
			#	print key + " is loved"
			#print song.get("rating", "WTF")
			if song.get('rating', "5") != '1' and song['deleted'] == False:
				if key in uniqueSongs:
					originalSong = uniqueSongs[key]
					counter += 1
					#if counter > 10:
					#	break
					#print "FOUND A DUPLICATE:" + key + " (" + originalSong["id"] + ")"
					
					#give up on getting fancy by removing the shorter song, just take the 2nd one found
					thumbsDownSongs.append(song)
					
					#if originalSong['estimatedSize'] > song['estimatedSize']:
					#	print key + " UP: " + originalSong['estimatedSize'] + " " + song['estimatedSize']
					#	thumbsDownSongs.append(song)
					#else:
					#	print key + " down: " + originalSong['estimatedSize'] + " " + song['estimatedSize']
						#TODO: for some reason, this append is not same type of "thing"
						#print originalSong["id"]
					#	thumbsDownSongs.append(originalSong)
						#thumbsDownSongs.append(api.get_track_info(uniqueSongs[key]["id"]))
				else:
					uniqueSongs[key] = song
	for x in thumbsDownSongs:
		print x['artist'] + " - " + x['title']
	
	#WARN: will make thumbs down
	#TODO: uncomment this line------------------
	#api.rate_songs(thumbsDownSongs, '1')
	print "found " + str(len(thumbsDownSongs)) + " dupe songs"
		
		
		#tracks = playlist['tracks']
		#find_and_remove_dups(api, tracks)

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
	dedupeSongs()
	api.logout()
else:
	print "Not logged in! Exiting..."
	exit(1)

print "Script has finished successfully!"

