import glob
import hashlib
import os
import shutil
import logging
import re

#---------Python 3-------------
#constants
#moviedirs = ["D:/video/family", "D:/video/movieseries", "D:/video/documentaries", "D:/video/unwatched", "D:/video/archivemovies"]
#baseMusicDirs = ["D:/My Music/Pop", "D:/temp/google_music_export/Tracks"]
baseMusicDirs = ["D:/My Music/Pop"]
#baseMusicDirs = ["d:/temp/fixmusic2"]
logfilePath = "c:/work/music/badmusic/"
allMovieFiles = []
targetMoveFolder = "c:/work/music/badmusic/"
#reFileExtention = re.compile('\.{mkv|mp4|avi}')
reFileExtention = re.compile('\\.(mp3)')
#reYear= re.compile([\[|\(]\d\d\d\d\)|\])
reYear= re.compile( '[\\[|\\(]\\d\\d\\d\\d[\\]|\\)]' )
reThe = re.compile('^the ', re.IGNORECASE)
reParens = re.compile('\\(.*\\)', re.IGNORECASE)
reSQBrackets = re.compile('\\[.*\\]', re.IGNORECASE)
reCharOnly = re.compile('![a-z]')
reOneInParens = re.compile('\\(1\\)')
reFEAT = re.compile('feat\\.([a-z]+)+',re.IGNORECASE)
reArtist = re.compile('^[a-z]+\\-', re.IGNORECASE)
#reFileExtention = re.compile('\.mkv')
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
            allMovieFiles.append([f, (root+"/"+f)])

def simpleMovieName(fileName):
    cleansedName = fileName.lower()
    cleansedName = re.sub(re.compile(' '), '', cleansedName)
    cleansedName = re.sub(reThe, '', cleansedName)
    cleansedName = re.sub(reFileExtention, '', cleansedName)
    
    cleansedName = re.sub(reYear, '', cleansedName)
    #test cleansedName = re.sub(reSQBrackets, '', cleansedName)
    #test cleansedName = re.sub(reParens, '', cleansedName)
    cleansedName = re.sub(reArtist, '', cleansedName)
    cleansedName = re.sub(reCharOnly, '', cleansedName)
    cleansedName = re.sub(re.compile('\\.'), '', cleansedName)
    cleansedName = re.sub(re.compile('^copyof'), '', cleansedName)
    cleansedName = re.sub(reOneInParens, '', cleansedName)
    cleansedName = re.sub(reFEAT, '', cleansedName)
    

    #reFileExtention
    #logger.debug('clean: ' + cleansedName)
    return cleansedName
            
def findDupes():
    matchCount = 0
    for file_name in allMovieFiles:
        #logger.debug("file:" + file_name[0])
        #if re.search(reFileExtention, file_name[0]) is not None:
        if re.search(reFileExtention, file_name[0]) is not None:
            filehash = simpleMovieName(file_name[0])
            #ORIG if filehash in filehashes:
            #look for inclusion AND on the C drive
            if (filehash in filehashes) and (file_name[1].lower().startswith("c:/work/")):
                #logger.info("collision! " + file_name[0] + "  == " + filehash)
                #best to move the file that has (1) at end
                fileToMove = file_name[1]
                
                #TODO: what is this?
                if re.search(reOneInParens, filehashes[filehash]) is not None:
                    logger.debug("has 111111 " + filehashes[filehash])
                    fileToMove=filehashes[filehash]
                logger.info("DUPE: " + file_name[1] + " ------ " + filehashes[filehash])
                asktoMove = input(f"Move File? {fileToMove}")
                if(asktoMove.lower() == 'q'):
                    break
                if(asktoMove.lower() == 'y'):
                    logger.info("do the move!")
                    duplicates.append({"filepath":fileToMove, "hash": filehash, "original":file_name[0]})
                    matchCount += 1
            else:
                filehashes[filehash] = file_name[1]
                #logger.debug ('new file found hash: ' + filehash + " for filename: " + file_name[1])
    logger.info('%(hits)i / %(all)i files' % {'hits': matchCount ,'all':len(allMovieFiles)})

def moveDupes() :
# do work with the duplicates
    for x in duplicates:
        outputDetails = "D file: " + x["filepath"] #+ "\n original: " + x["original"]
        logger.debug("working on this:" + outputDetails)
        logger.info(outputDetails)
        try:
            shutil.move(x["filepath"], targetMoveFolder)
        except (IOError) as why:
            logger.error(x["filepath"] + " already exists in target, try removing instead")
            #os.remove(x["filepath"])        


###############################################
##MAIN
#global vars
logger = prepLogger("dupeMovieFile")    
filehashes = dict()
duplicates = list()

logger.info("load a list of files")

for md in baseMusicDirs:
    all_files_from_path_gen(md)
findDupes()
moveDupes()
logger.info("size of hashes file:" + str(len(filehashes)))