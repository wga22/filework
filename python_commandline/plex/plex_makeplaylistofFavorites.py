'''
Nov 2021 - write out all playlists to both winamp and moode
May 2021 - Makes a playlist from 4 star files
May 2025 - write out all playlists - include Moode
[
{"service":"mpd","uri":"mnt/NAS/Spiderman/Billie Eilish/Billie Eilish - everything i wanted.mp3","title":"ee","artist":"be","album":"badss"},
{"service":"mpd","uri":"mnt/NAS/Spiderman/Blind Melon/Blind Melon - No Rain.mp3","title":"No Rain","artist":"Blind Melon","album":"Blind Melon","albumart":"/albumart?cacheid=236&web=Blind%20Melon/Blind$
{"service":"mpd","uri":"mnt/NAS/Spiderman/Britney Spears/Britney Spears - Baby One More Time.mp3",
"title":"Baby One More Time"}
]

TODO: include linux and windows versions

'''
import re
import os
import logging
#from plexapi.myplex import MyPlexAccount   https://python-plexapi.readthedocs.io/en/latest/index.html
from plexapi.server import PlexServer
import json

JSON_PATH='./plex/plex_credentials.json'

rePlexPathPrefix = re.compile('/media/ten/music/Pop') 
reQuotes = re.compile('"')
reWhitespace = re.compile('\\s')

#folders to write playlists into
winampPlaylistFolder="D:/My Music/playlists/"
moodePlaylistDirName="C:/work/music/playlistwork/playlist/"
SongDirName="D:/My Music/Pop"

#path for each to get music from 
volBasePath = "mnt/NAS/spiderman"
moodeBasePath = "NAS/Spiderman-POP"
winampSongDirBasePath="D:/\"My Music\"/Pop"

# BEFORE: /media/ten/music/Pop/The Who/The Who 
# AFTER: mnt/NAS/Spiderman/Billie Eilish/Billie Eilish - everything i wanted.mp3

def clearQuotes(fieldValue):
	return re.sub(reQuotes, "", fieldValue)
	return _logger

def checkPaths():
    print(winampPlaylistFolder, " ", os.path.exists(winampPlaylistFolder))
    print(moodePlaylistDirName, " ", os.path.exists(moodePlaylistDirName))
    return os.path.exists(winampPlaylistFolder) and os.path.exists(moodePlaylistDirName)

def main():
    with open(JSON_PATH) as json_file:
        plex_cred = json.load(json_file)
        plex = PlexServer(plex_cred['baseurl'], plex_cred['token'])
        for playlist in plex.playlists():
            playlistLen = 0        
            try:
                playlistLen = len(playlist.items())
            except:
                print("Cannot get the length of songs in ", playlist.title)
            #make for music playlists, with more than 10, less than 500
            if playlistLen < 3000 and playlistLen > 10 and ('track' == playlist.items()[0].TYPE):
                listName=re.sub(reWhitespace, "",playlist.title)
                winPLSFileName=winampPlaylistFolder + listName + ".m3u"
                moodePLSFileName= moodePlaylistDirName + listName + ".m3u"
                print ("making playlist all songs from: ", playlist.title, " ", winPLSFileName, " len:", str(playlistLen))
                winampPlaylist = open(winPLSFileName , "w")
                moodePlaylist = open(moodePLSFileName , "w")
                               
                for song in playlist.items():
                    print("writing out the playlist ",playlist.title )
                    try:
                        # print(song.artist().title , " - " ,  song.title )
                        # working url, title, key
                        #print("parts: " , song.media[0].parts[0])
                        fileName = song.media[0].parts[0].file
                        winampFileName =  re.sub(rePlexPathPrefix, winampSongDirBasePath, fileName)
                        moodeFileName = re.sub(rePlexPathPrefix, moodeBasePath, fileName)
                        fileName = re.sub(rePlexPathPrefix, volBasePath, fileName)
                        print(song.media[0].parts[0].file , " - " ,  fileName )
                        try:
                            # TODO - since running on windows, test for the file first on windows?
                            winampPlaylist.write(clearQuotes(winampFileName)+'\n')
                            moodePlaylist.write(clearQuotes(moodeFileName)+'\n')
                        except:
                            print("error writing %s", fileName)
                    except:
                        print("ERROR PULLING THE SONG ", song.title)
                    #element = "{"+selection.media[0].parts[0].file.split('/')[-1]+"}"
                    #fileItem = plex.fetchItem(song.key)
                    #print(fileItem.url  )
                    #TODO - make it actually find the file first
                winampPlaylist.close()
                moodePlaylist.close()

if checkPaths():
    main()
else:
    print("one or more of the paths do not exist")


   
'''
filename = re.sub(validfilenameRE, '_', filename)
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler('d:/temp/python_log.txt')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)
logger.info('While this is just chatty')
'''