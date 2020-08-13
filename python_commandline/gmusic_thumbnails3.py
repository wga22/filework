#!/usr/bin/env python
from gmusicapi import Mobileclient
from PIL import Image
import requests
from io import BytesIO
import sys
import time
import re

'''
 author: Will Allen
 purpose: work with thumbnails on the gmusicap
	- replace empty thumnails
	-replace thumbnails that match certain specified types
 https://unofficial-google-music-api.readthedocs.io/en/latest/

D:\devapps\Python2\python.exe gmusic_thumbnails.py
'''

BADURL={
"http://lh5.ggpht.com/zAQ250IwD_eR8C-B56fD6nT0LBxMxWdALUrWXH0NUVOcG6jKOcI9MbRGoioWww",
"http://lh3.googleusercontent.com/TgligzpXxzsmN4urb_tGqG7_G0upsGByVc6T1Q5qysqOn0DpkTYumQznkRg",
"http://lh6.ggpht.com/_KQLqM0kybdSfqswwwP2NlvO7moafJZz6VTtH09aJdMiCPQ_XdmoJOJo8DT3yw",
"http://lh5.ggpht.com/5gIxpaN4Aix7aVpYV_KlRVRqbr42U43Vw7pibkQcL6UoyhmHejOAiLka_q0u",
"http://lh5.ggpht.com/BTW1QeYcaJ-BUcVeHY4VprC2eOh81YeewRg7tZ8n8QBG-X7B90LbUNWELzzTpA",
"http://lh6.ggpht.com/guqAGiEwCzQfSj1bRDPAVpqbnL1gBhTaYi_5bRZwXgNKl5mi5SN1cewOxWk",
"http://lh3.ggpht.com/SEzpu5OwoR6h05YbrltJogcTrHMRNpKNEiyIVAAwYJli5eFkZUozWV6kZyc",
"http://lh4.ggpht.com/t0w2VwAv9y1wBzovGlkY6ncfVVIBmQj4JPV4NuMbbUaX_BC821XNxTfZdafkgw",
"http://lh5.ggpht.com/yQbUvEiOnz3QBGDY_cmH5GVr8cBkDrDX1W2Ysk1ux7y8OEbPnUaS_356F4kE4g",
"http://lh3.ggpht.com/0vsTj2Ty8oNh-Xe6NR67etFj-VIH__EXJeQM4RJDuHy4Nqgu3gr5-E7Zkh4",
"http://lh3.ggpht.com/HpMhblQ_JGkSlO7POKm9GSrVGo99zNuAp7rZE0R3tdlml_IB8t3HTGpRkRdq",
"http://lh3.ggpht.com/OoljY2u73sCazFLaynrIwG0aEp3g5LJk58-La2-I8pV-g1lDVc8fyPlEtPI",
"http://lh6.ggpht.com/8yGyoeX1OK3yReV8BB8YJE9s2faky34E0wvPL7H5fjcwAvjhqF0aepC-KH-WJw",
"http://lh5.ggpht.com/KU6DPMHB8sPJBeMB95nxGGPrQbYBvKCnxJXl30GH8z4bX_4VgUMSApjzpo8",
"http://lh3.googleusercontent.com/EJ7rY7pKRljwkZxyy7k6FFonRVPBLBV58oKx_PkJIdxeG1p8QDsePxiBaKOr",
"http://lh3.googleusercontent.com/oQs3BUStFnuOPPRDOYCHF-08-UoG0PfdD2ppkVyUN-qSeg8-_iF964WXGXEx"
}

BADHASHES = {
"14e8696969b23071",
"33ab4d55554d2bcd",
"1627973718302040",
"3b193d2d3d3c1c12",
"8c131b0f070f07c0",
"d8e6e692921a6870",
"c4e6ce9a99d3dbcf"
}

### Functions
def workTheTracks(tracks):
	for track in tracks:
		tries = 0
		trackId = track['trackId']
		entryId = track['id']
		output( track )

def dhash(imageURL, hash_size = 8):
	#https://blog.iconfinder.com/detecting-duplicate-images-using-python-cb240b05a3b6
        # Grayscale and shrink the image in one step.
	image = 1
	try:
		response = requests.get(imageURL)
		image = Image.open(BytesIO(response.content))
		#image = Image.open(imageURL)
	except:
		output( "couldnt open the URL" )
		return "0"
	image = image.convert('L').resize((hash_size + 1, hash_size), Image.ANTIALIAS,  )
	pixels = list(image.getdata())
# Compare adjacent pixels.
	difference = []
	for row in xrange(hash_size):
		for col in xrange(hash_size):
			pixel_left = image.getpixel((col, row))
			pixel_right = image.getpixel((col + 1, row))
			difference.append(pixel_left > pixel_right)
# Convert the binary array to a hexadecimal string.
			decimal_value = 0
			hex_string = []
			for index, value in enumerate(difference):
				if value:
					decimal_value += 2**(index % 8)
				if (index % 8) == 7:
					hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
					decimal_value = 0
	return ''.join(hex_string)

def output(printMe):
	print(printMe)

def main():
	songLists = api.get_all_songs(True, False)
	annoying = 0
	exceptionCount = 0
	noAlbumArt = 0
	for songs in songLists:
		for song in songs:
			#print song
			#print song["comment"]
			if song.has_key("albumArtRef") and len(song["albumArtRef"]) > 0:
				songAlbumURL = song["albumArtRef"][0]["url"]
				if len(songAlbumURL) > 0:
					#print songAlbumURL
					imageHash = dhash(songAlbumURL)
					if songAlbumURL in BADURL or imageHash in BADHASHES:
						title = song['title']
						artist = song['artist']
						key = artist +"-"+ title
						output( key + " has the annoying albumart" )
						annoying += 1
						BADHASHES.add(imageHash)
						output( "Removing album art from: " + key)
						del song["albumArtRef"]
						api.change_song_metadata(song)
						return
			else:	
				noAlbumArt += 1
					

				#else:
				#	print key + " is clean"
					
	output( "Bad Album Art: " + str(annoying))
	output( "No Album Art: " + str(noAlbumArt))
	output( "Exceptions: " + str(exceptionCount))
	output( "--------------------------------")
	output( BADHASHES )
	
			#title = stripString(song['title'], False)
			#artist = stripString(song['artist'], True)
			#key = artist +"-"+ title
			#print "Song: " + title + " - " + artist
			#if key in uniqueSongs and song['rating'] != '1' and song['deleted'] == False:
			#if song.get('rating', "5") != '1':
			#	print key + " is loved"
			#print song.get("rating", "WTF")
	'''
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
	'''	
		
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
	output( "No OAuth credentials found! Please setup in the following screen!" )
	api.perform_oauth()
	api.oauth_login(Mobileclient.FROM_MAC_ADDRESS) # If it fails here, it wasn't meant to be

# Then, move on to doing all the work
if api.is_authenticated():
	main()
	api.logout()
else:
	output( "Not logged in! Exiting..." )
	exit(1)

output( "Script has finished successfully!" )

