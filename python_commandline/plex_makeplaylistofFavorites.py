'''
Feb 2021 - deletes all songs from plex attached via JSON that are rated 1 star

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
PLAYLISTROOT="D:/My Music/Pop/"

with open('plex_credentials.json') as json_file:
    plex_cred = json.load(json_file)
    #account = MyPlexAccount(plex_cred.user, plex_cred.password)
    #plex = account.resource(plex_cred.server).connect()  # returns a PlexServer instance
    #print(plex_cred)
    #print(plex_cred['baseurl'])
    plex = PlexServer(plex_cred['baseurl'], plex_cred['token'])
    for playlist in plex.playlists():
        if("4 stars" == playlist.title):
            print ("making playlist all songs from: ", playlist.title)
            for song in playlist.items():
                print(song.artist().title , " - " ,  song.title )
                #TODO - make it actually find the file first
                newPlaylist.write(PLAYLISTROOT + song.artist().title +"/"+ song.artist().title + " - " +  song.title + .mp3\n")
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