#!/usr/bin/env python
from gmusicapi import Mobileclient
from gmusicapi import Webclient
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
celine = "http://lh5.ggpht.com/uRm9B06VVnxJawdkoeq6IiZ9iFMnShBXDmLPrgmEdzAunXNIuPn8JXDF7mU"
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
		print track

def dhash(imageURL, hash_size = 8):
	#https://blog.iconfinder.com/detecting-duplicate-images-using-python-cb240b05a3b6
        # Grayscale and shrink the image in one step.
	image = 1
	try:
		response = requests.get(imageURL)
		image = Image.open(BytesIO(response.content))
		#image = Image.open(imageURL)
	except:
		print "couldnt open the URL"
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


def writeOutBadAlbumArtSongs():
	songLists = mc.get_all_songs(True, False)
	annoying = 0
	exceptionCount = 0
	listOfSongs = []
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
						print key
						print imageHash
						print songAlbumURL
						print "XXXXXXXXXXXXXXXXXXXX"
						annoying += 1
						BADHASHES.add(imageHash)
						listOfSongs.append(song["id"])
						#print "Removing album art from: " + key
						#print song
						#print song["albumArtRef"][0]
						#print "------------"
						#noluck del song["albumArtRef"]
						#noluck song["albumArtRef"][0]["url"] = ""
						#noluck song["albumArtRef"][0] = {"url":celine}
						#noluck song["albumArtRef"] = []
						#noluck song["albumArtRef"] = None
						#DOCS SAY DOESNT WORK api.change_song_metadata(song)
						#print "XXXXXXXXXXXXXXXXXXXX"
						#print song
						#print song["albumArtRef"][0]
						#return
			else:	
				noAlbumArt += 1
					

				#else:
				#	print key + " is clean"
					
	print "Bad Album Art: " + str(annoying)
	print "No Album Art: " + str(noAlbumArt)
	print "Exceptions: " + str(exceptionCount)
	print "--------------------------------"
	print BADHASHES
	DOWORK = True
	if DOWORK and len(listOfSongs) > 0:
		badArtPlaylist = [p for p in mc.get_all_playlists() if p.get('name') == 'FIX ALBUM ART']
		print "adding these "+str(len(listOfSongs))+" songs to " + badArtPlaylist[0]["name"]
		mc.add_songs_to_playlist(badArtPlaylist[0]["id"], listOfSongs)
	#end writeOutBadAlbumArtSongs

def writeAlbumArt():
	#TODO: https://github.com/simon-weber/gmusicapi/issues/352
	# see branch: https://github.com/simon-weber/gmusicapi/issues/242
	wc = Webclient()
	wc.__init__()
	#wc.oauth_login(Mobileclient.FROM_MAC_ADDRESS)
	if wc.login(uname, password):
		print "webclient login successful"
	else:
		print "LOGIN FAILED for Webclient"
		#	Webclient.upload_album_art(song_ids, image_filepath)

def printPlaylists():
	#mm = Musicmanager()
	#mm.perform_oauth()
	for pl in mc.get_all_playlists():
		print pl["id"] + " - " + pl["name"]
		#print pl

def main():
	writeOutBadAlbumArtSongs()
	#writeAlbumArt()
	#printPlaylists()	
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
mc = Mobileclient()
mc.__init__()

# Check to see if OAuth credentials available, ask user to setup if not
try:
	mc.oauth_login(Mobileclient.FROM_MAC_ADDRESS)
	#api.perform_oauth()
except:
	print "No OAuth credentials found! Please setup in the following screen!"
	mc.perform_oauth()
	mc.oauth_login(Mobileclient.FROM_MAC_ADDRESS) # If it fails here, it wasn't meant to be

# Then, move on to doing all the work
if mc.is_authenticated():
	main()
	mc.logout()
else:
	print "Not logged in! Exiting..."
	exit(1)

print "Script has finished successfully!"


'''
48c88c2e-986b-47b2-9a7e-53f746522902 - Randomness
5f1d870d-784d-479b-bd8c-4df83de954bd - Christmas
d5076cbf-cd0b-4cd0-81fb-3dfb2fd91766 - Winter Mix
8f70cd2e-9e69-4225-b57a-6427871cd55a - Maroon 5 danielle
05a87d67-530f-43d6-9e29-0248e10f8774 - Rihanna
75fd2980-1df6-40ac-8020-3db4ab851315 - wonderwall mix
7a38b409-2be9-4e73-baea-c374c0e3b5cf - Danica
6c1e2903-c2c7-4fda-ac23-c0f2d04fce99 - Christmas best
84c4704f-51a9-44db-8f35-4caf1456f304 - Radiohead
34405f7b-6322-417b-a19e-f7a35997948a - Deadmau5
51818758-a8fe-410c-9ec6-61797c184a6a - All time favorites
884fcf21-6cc9-4275-b5a2-4123f32afc53 - Digital Remixes
f7fad7b7-d004-492c-8721-c327c028889b - Modern POP Favs
256ff848-90b4-39a7-9890-df56714ba704 - Springtime - D&D
b5094625-fccd-45f6-bbc8-5c0952647e90 - Marshmello
d298a9a6-5f23-4f0e-b809-3f00f3262e73 - No Time to Sleep
01274c09-233f-48ca-b00a-e0c21a14ac26 - Classic Rock
3739eec1-b330-4819-8033-453f778107db - Phil, u2, elton, police
6a3d86bd-c3a3-4e16-a8bf-7791968d0b31 - Swedish house and David g
69872533-4970-4a3c-b8a8-c3774b2f9b16 - Yacht Rock
4166fdc6-fdd3-4439-806b-e397a081f206 - Pool Party
d9adb55b-d16d-428e-97cc-7780b7afb6f0 - Mellow College
e0564d30-3d8a-4c0d-ac14-a6467c9b16c4 - Alternative 80's
918e5e43-ded4-4ce7-a68a-60235b30213e - Sun and moon
ac7cba63-71c6-402a-8c66-7ac6d385dcdd - Pink led
f1def98d-b35f-4a00-98b7-b61fa6218393 - Pop Hits -2010's
84c87281-5618-4612-abb8-ee15d1b9192e - Hip hop Paris
5b6d559a-bd7c-470f-8bca-b18c03fcc0f7 - FIX ALBUM ART
b42ddbfb-397d-4980-b59e-84a651220435 - Movin and Groovin
3e12c066-5d4e-40b1-987f-21dbf65123ab - Ballads
167cb66a-a0cc-4abc-a9c9-8bf34487d7f7 - R&B
032e8dd8-8f0d-43cb-bfc3-98d60dcc3d03 - George Michael
2a7d5202-70fc-49df-a752-019fe4c9f60e - Hall and Oates
Script has finished successfully!
'''