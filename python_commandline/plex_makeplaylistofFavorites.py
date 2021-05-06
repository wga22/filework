'''
May 2021 - Makes a playlist from 4 star files

[
{"service":"mpd","uri":"mnt/NAS/Spiderman/Billie Eilish/Billie Eilish - everything i wanted.mp3","title":"ee","artist":"be","album":"badss"},
{"service":"mpd","uri":"mnt/NAS/Spiderman/Blind Melon/Blind Melon - No Rain.mp3","title":"No Rain","artist":"Blind Melon","album":"Blind Melon","albumart":"/albumart?cacheid=236&web=Blind%20Melon/Blind$
{"service":"mpd","uri":"mnt/NAS/Spiderman/Britney Spears/Britney Spears - Baby One More Time.mp3",
"title":"Baby One More Time"}
]

'''
import re
import glob
import hashlib
import os
import shutil
import logging
import email
import mimetypes
#from plexapi.myplex import MyPlexAccount   https://python-plexapi.readthedocs.io/en/latest/index.html
from plexapi.server import PlexServer
import json
newPlaylistFile="D:/temp/favoritesfromplex.m3u"
newPlaylist = open(newPlaylistFile, "w")
cleanFilePath = re.compile('\/media\/ten\/music\/Pop') 
reQuotes = re.compile('"')
basePath = "mnt/NAS/Spiderman"
# BEFORE: /media/ten/music/Pop/The Who/The Who 
# AFTER: mnt/NAS/Spiderman/Billie Eilish/Billie Eilish - everything i wanted.mp3
PLAYLISTROOT="D:/My Music/Pop/"

def clearQuotes(fieldValue):
	return re.sub(reQuotes, "", fieldValue)
	return _logger


with open('plex_credentials.json') as json_file:
    plex_cred = json.load(json_file)
    #account = MyPlexAccount(plex_cred.user, plex_cred.password)
    #plex = account.resource(plex_cred.server).connect()  # returns a PlexServer instance
    #print(plex_cred)
    #print(plex_cred['baseurl'])
    plex = PlexServer(plex_cred['baseurl'], plex_cred['token'])
    newPlaylist.write("[")
    for playlist in plex.playlists():
        if("4 stars" == playlist.title):
            print ("making playlist all songs from: ", playlist.title)
            for song in playlist.items():
                #print(song.artist().title , " - " ,  song.title )
                # working url, title, key
                fileName = song.media[0].parts[0].file
                fileName = re.sub(cleanFilePath, basePath, fileName)
                #print(song.media[0].parts[0].file , " - " ,  fileName )
                element = '{"service":"mpd","uri":"'+clearQuotes(fileName)+'","title":"'+clearQuotes(song.title)+'", "artist":"'+clearQuotes(song.artist().title)+'"},\n'
                print(element)
                newPlaylist.write(element)
                #element = "{"+selection.media[0].parts[0].file.split('/')[-1]+"}"
                #fileItem = plex.fetchItem(song.key)
                #print(fileItem.url  )
                #TODO - make it actually find the file first
                #newPlaylist.write(PLAYLISTROOT + song.artist().title +"/"+ song.artist().title + " - " +  song.title + .mp3\n")
    newPlaylist.write("]")
    newPlaylist.close()

'''
    for song in plex.search('various', 'artist'):
        if(song.TYPE=='track'):
            artist = song.artist()
            artistName = 'null' if  artist is None else artist.title
            album = song.album()
            if album is None:
                albumName = 'null' 
                albumArtistName = 'null'
            else:
                albumName = album.title
                albumArtistName = 'null' if album.artist() is None else album.artist().title
            print('%s --- %s -----%s ----- %s' % (artistName, albumArtistName, albumName, song.title))
            #print('%s (%s)' % (, song.TYPE))
        elif (song.TYPE=='artist'):
            print('artist: %s', song.title )
            for album in song:
                print("album title: %s", album.title )


filename = re.sub(validfilenameRE, '_', filename)
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('d:/temp/python_log.txt')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)
logger.info('While this is just chatty')
'''