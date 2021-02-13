'''
utility to load a file of song names(songsToRemoveFile), and then move them out of music library(baseMusicDirs) to a "targetMoveFolder" folder
'''
import glob
import hashlib
import os
import shutil
import logging
import re

#constants
baseMusicDirs = ["D:/My Music/Pop"]
logfilePath = "d:/temp/"
songsToRemoveFile = "d:/temp/playlistwork/badsongs_2021-2.txt"
targetMoveFolder = "D:/temp/badmusic/"

#Globals
songsToRemove=dict()

#constants = compile once the re for the filename cleanse
reFileExtention = re.compile('\.(mp3)')
reYear= re.compile( '[\[|\(]\d\d\d\d[\]|\)]' )
reThe = re.compile('^the ', re.IGNORECASE)
reSQBrackets = re.compile('\[.*\]', re.IGNORECASE)
reCharOnly = re.compile('![a-z]')

def prepLogger(appName):
	_logger = logging.getLogger(appName)
	hdlr = logging.FileHandler(logfilePath + "python_"+appName+"log.txt")
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	_logger.addHandler(hdlr) 
	_logger.addHandler(logging.StreamHandler())
	_logger.setLevel(logging.INFO)
	return _logger


def simpleMovieName(fileName):
    cleansedName = fileName.lower()
    cleansedName = re.sub("\r?\n", "", cleansedName)
    cleansedName = re.sub(reThe, '', cleansedName)
    cleansedName = re.sub(reFileExtention, '', cleansedName)
    cleansedName = re.sub(reYear, '', cleansedName)
    cleansedName = re.sub(reSQBrackets, '', cleansedName)
    cleansedName = re.sub(reCharOnly, '', cleansedName)
    cleansedName = re.sub(re.compile('\.'), '', cleansedName)
    cleansedName = re.sub(re.compile(' '), '', cleansedName)
    #reFileExtention
    #logger.debug('clean: ' + cleansedName)
    return cleansedName


def loadBadSongs() :
    f = open(songsToRemoveFile, "r")
    _bs = dict()
    badSong = ""
    for x in f:
        badSong = simpleMovieName(x)
        #logger.info("bad song: ", badSong)
        #logger.info("bad song: ", x)
        logger.debug("adding song: " + badSong)
        #_bs.append(badSong)
        _bs[badSong] = True
    f.close()
    return _bs

#yield os.path.join(root, d, f)
def all_files_from_path_gen(p, dictBadS):
    print("all files: " + p)
    retfiles = []
    matchCount = 0
    for root, dirs, files in os.walk(p, topdown=False):
        for file in files: 
        #for d in os.walk(dirs):
            #retfiles.extend(all_files_from_path_gen(root+d))
            if re.search(reFileExtention, file) is not None:
                cleanfileName = simpleMovieName(file)
                #logger.debug("check file: " +fileName)
                if cleanfileName in dictBadS:
                    matchCount += 1
                    fullPath = os.path.join(root, file)
                    logger.info("Moving found file: " + fullPath)
                    shutil.move(fullPath, targetMoveFolder)
    logger.info('matches %(hits)i /  total: %(all)i files' % {'hits': matchCount , 'all':len(dictBadS)})
    #logger.info('%(hits)i / %(all)i files' % {'hits': noMatchCount ,'all':len(dictBadS)})
    
    

###############################################
##MAIN
#global vars
logger = prepLogger("deleteBadMusic")	
logger.info("load a list of files")
songsToRemove = loadBadSongs()

for md in baseMusicDirs:
	all_files_from_path_gen(md, songsToRemove)

