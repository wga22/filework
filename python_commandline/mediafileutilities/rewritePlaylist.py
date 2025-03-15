'''
load a playlist file
search for the actual location of the song (take liberties?)
rewrite out a new playlist with found songs
'''

import glob
import hashlib
import os
import shutil
import logging
import re
from pathlib import Path

#constants
#baseMusicDirs = ["D:/My Music/Pop", "D:/temp/google_music_export/Tracks"]
baseMusicDirs = ["D:/My Music/Pop"]
oldPlaylistFile="D:/temp/playlistwork/playlist/garage2021.m3u"
newPlaylistFile="D:/temp/garage2021.m3u"
logfilePath = "d:/temp/"
allMusicFiles = []

reFileExtention = re.compile('\.(mp3)')
#reYear= re.compile([\[|\(]\d\d\d\d\)|\])
reYear= re.compile( '[\[|\(]\d\d\d\d[\]|\)]' )
reThe = re.compile('^the ', re.IGNORECASE)
reSQBrackets = re.compile('\[.*\]', re.IGNORECASE)
reCharOnly = re.compile('![a-z]')
reComment = re.compile('^#.*')
#reFileExtention = re.compile('.*')

def prepLogger(appName):
    _logger = logging.getLogger(appName)
    hdlr = logging.FileHandler(logfilePath + "python_"+appName+"log.txt")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    _logger.addHandler(hdlr) 
    _logger.addHandler(logging.StreamHandler())
    _logger.setLevel(logging.DEBUG)
    return _logger

#yield os.path.join(root, d, f)
def all_files_from_path_gen(p):
    print("all files: " + p)
    retfiles = []
    for root, dirs, files in os.walk(p, True):
        #for d in dirs:
            #logger.debug("add directory: " +d)
            #retfiles.extend(all_files_from_path_gen(root+d))
        for f in files:
            allMusicFiles.append([f, (root+"/"+f)])

def simpleMovieName(fileName):
    cleansedName = fileName.lower()
    cleansedName = re.sub(re.compile(' '), '', cleansedName)
    cleansedName = re.sub(reThe, '', cleansedName)
    cleansedName = re.sub(reFileExtention, '', cleansedName)
    #cleansedName = re.sub(reYear, '', cleansedName)
    #cleansedName = re.sub(reSQBrackets, '', cleansedName)
    cleansedName = re.sub(reCharOnly, '', cleansedName)
    cleansedName = re.sub(re.compile('\.'), '', cleansedName)
    cleansedName = re.sub(re.compile('\r'), '', cleansedName)
    cleansedName = re.sub(re.compile('\n'), '', cleansedName)
    cleansedName = re.sub(re.compile('^copyof'), '', cleansedName)
    #reFileExtention
    #logger.debug('clean: ' + cleansedName)
    return cleansedName

def baseFile(fileName):
    p = Path(fileName)
    #logger.debug(p)
    return p.name


def writeNewPlaylist():
    matchCount = 0

    #make hash of the cleaned filenames
    for file_name in allMusicFiles:
        hashName = simpleMovieName(file_name[0])
        filehashes[hashName] = file_name[1]
        logger.debug(hashName + " -full file path:" + file_name[1])

    # read the playlist
    songsToFind = list()
    oldPlaylist = open(oldPlaylistFile, "r")
    newPlaylist = open(newPlaylistFile, "w")
    for x in oldPlaylist:
        if re.search(reComment, x) is None and len(x)>0:
            songOnly = simpleMovieName(baseFile(x))
            #logger.debug("add Song to List %s ", songOnly)
            if songOnly in filehashes :
                songsToFind.append(songOnly)
                newPlaylist.write(filehashes[songOnly] + "\n")
                logger.info("found %s for the list", songOnly)
            else:
                logger.info("couldnt find %s", songOnly)



    oldPlaylist.close()
    newPlaylist.close()
    
   

    
    
    
    
'''
            for z in filehashes:
                #logger.debug("[" + z + "]=?[" + songOnly + "]")
                #logger.debug(str(len(z)) + "=?" + str(len(songOnly)))
                if z == songOnly:
                    logger.debug("YIPPPPEE" + songOnly)


    for x in songsToFind:
        simplifiedName = simpleMovieName(songsToFind[x])
        if simplifiedName in 


    for file_name in allMusicFiles:
        #logger.debug("file:" + file_name[0])
        #if re.search(reFileExtention, file_name[0]) is not None:
        if re.search(reFileExtention, file_name[0]) is not None:
            filehash = simpleMovieName(file_name[0])
            if filehash in filehashes:
                matchCount += 1
                #logger.info("collision! " + file_name[0] + "  == " + filehash)
                #best to move the file that has (1) at end
                fileToMove = file_name[1]
                if re.search(reOneInParens, filehashes[filehash]) is not None:
                    logger.debug("has 111111 " + filehashes[filehash])
                    fileToMove=filehashes[filehash]
                duplicates.append({"filepath":fileToMove, "hash": filehash, "original":file_name[0]})
                logger.info("DUPE: " + file_name[1] + " ------ " + filehashes[filehash])
            else:
                filehashes[filehash] = file_name[1]
                #logger.debug ('new file found hash: ' + filehash + " for filename: " + file_name[1])
    logger.info('%(hits)i / %(all)i files' % {'hits': matchCount ,'all':len(allMusicFiles)})
'''

###############################################
##MAIN
#global vars
logger = prepLogger("rewritePlaylistFile")    
filehashes = dict()
duplicates = list()

logger.info("load a list of files")

#pull full music library
for md in baseMusicDirs:
    all_files_from_path_gen(md)
writeNewPlaylist()
logger.info("size of hashes file:" + str(len(filehashes)))

'''

'''
        
'''
prices = {'apple': 0.40, 'banana': 0.50}
my_purchase = {
    'apple': 1,
    'banana': 6}
grocery_bill = sum(prices[fruit] * my_purchase[fruit]
       for fruit in my_purchase)


filehashes = ['asdfs']
for f in filehashes
    #print(fh, "=", filehashes[fh])
    print("lop")

import glob
# glob supports Unix style pathname extensions
python_files = glob.glob('*.py')
for file_name in sorted(python_files):
    print '    ------' + file_name

    with open(file_name) as f:
        for line in f:
            print '    ' + line.rstrip()

    print

def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()        
    
    
    '''
