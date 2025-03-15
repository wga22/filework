'''
June 2021 - list songs in each playlist and songs with each rating - data manually exported to Plex Music Library Stats in google docs
https://docs.google.com/spreadsheets/d/1C-OpKVWlOcQPE0g0j1XoIsn-9ru6Fhmnd4IiHH9dpZk/edit#gid=0

reset token by opening "XML" of a doc and looking at end of querystring.

❤️ Artist  has songs:  4152
Cannot get the length of songs in  ❤️ Tracks
❤️ Tracks  has songs:  0
4 stars  has songs:  347
80's  has songs:  154
All Music  has songs:  4152
BAD_MUSIC  has songs:  65
Fresh ❤️  has songs:  806
Haven't heard in Months  has songs:  347
Millennium  has songs:  2936
No rating  has songs:  2387
Recently Added  has songs:  0
Cannot get the length of songs in  Recently Played
Recently Played  has songs:  273
Sun!  has songs:  38
Unplayed  has songs:  100
unrated  has songs:  4152
Aerial Videography  has songs:  8
Alternative 80's  has songs:  51
Arrow  has songs:  95
Ballads  has songs:  15
Classic Rock  has songs:  23
Danica fav  has songs:  17
Danica Good songs  has songs:  26
Danica Lyrical Songs  has songs:  8
Doobie Brothers  has songs:  12
Elton  has songs:  20
FIX ALBUM ART  has songs:  164
George Michael  has songs:  15
Hall and Oates  has songs:  8
Hip hop Paris  has songs:  17
Leave No Trace  has songs:  2
Love songs  has songs:  9
Mellow College  has songs:  16
Modern POP Favs  has songs:  17
Movin and Groovin  has songs:  15
Oldies  has songs:  28
Phil, u2, elton, police  has songs:  127
Pink led  has songs:  77
Pool Party  has songs:  4
Pop Hits -2010's  has songs:  10
R&B  has songs:  21
Radiohead  has songs:  15
Rihanna  has songs:  9
Summer  has songs:  34
Will Thumbs Up  has songs:  74
Winter Mix  has songs:  25
Yacht Rock  has songs:  12

'''
import os
import shutil
import logging
import mimetypes
#from plexapi.myplex import MyPlexAccount   https://python-plexapi.readthedocs.io/en/latest/index.html
from plexapi.server import PlexServer
import json

def playlistCounts():
    for playlist in plex.playlists():
        playlistLen = 0        
        try:
            playlistLen = len(playlist.items())
            print(playlist.title, "\t", str(playlistLen))
        except:
            print("Cannot get the length of songs in ", playlist.title)
        #make for music playlists, with more than 10, less than 500

def starCounts(libr):
    totalRatedSongs = 0
    for x in range(10):
        y=x+1
        thisRating = len(libr.search(libtype='track', userRating=y))
        totalRatedSongs += thisRating
        print(str(y/2), " stars\t", str(thisRating))
    print("all rated Songs: ", str(totalRatedSongs))
with open('plex_credentials.json') as json_file:
    plex_cred = json.load(json_file)
    #account = MyPlexAccount(plex_cred.user, plex_cred.password)
    #plex = account.resource(plex_cred.server).connect()  # returns a PlexServer instance
    #print(plex_cred)
    #print(plex_cred['baseurl'])
    plex = PlexServer(plex_cred['baseurl'], plex_cred['token'])
    playlistCounts()
    starCounts(plex.library)
    
    #TODO - write data directly to google docs!!https://erikrood.com/Posts/py_gsheets.html
    #TODO - or write data to DB to pull from apache?!
    #TODO - write it to a file, so cut paste to google docs easier
        
'''
        playlistLen = len(playlist.items())
        if playlistLen < 500:
            playFileName=newPlaylistFileDir + playlist.title + ".json"
            print ("making playlist all songs from: ", playlist.title, " ", playFileName, " len:", playlistLen)


        if playlistLen < 500:
'''
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