import glob
import hashlib
import os
import shutil
import logging
import re
import eyed3

#constants
#moviedirs = ["D:/video/family", "D:/video/movieseries", "D:/video/documentaries", "D:/video/unwatched", "D:/video/archivemovies"]
#baseMusicDirs = ["D:/My Music/Pop", "D:/temp/google_music_export/Tracks"]
#baseMusicDirs = ["D:/My Music/Pop"]
baseMusicDirs = ["d:/temp/fixmusic2"]
logfilePath = "d:/temp/"
allMovieFiles = []
targetMoveFolder = "D:/temp/musicfolders/"
#reFileExtention = re.compile('\.{mkv|mp4|avi}')
reFileExtention = re.compile('\.(mp3)')
#reYear= re.compile([\[|\(]\d\d\d\d\)|\])
reYear= re.compile( '[\[|\(]\d\d\d\d[\]|\)]' )
reThe = re.compile('^the ', re.IGNORECASE)
reSQBrackets = re.compile('\[.*\]', re.IGNORECASE)
reCharOnly = re.compile('![a-z]')
reOneInParens = re.compile('\(1\)')
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
    #cleansedName = re.sub(reYear, '', cleansedName)
    #cleansedName = re.sub(reSQBrackets, '', cleansedName)
    cleansedName = re.sub(reCharOnly, '', cleansedName)
    cleansedName = re.sub(re.compile('\.'), '', cleansedName)
    cleansedName = re.sub(re.compile('^copyof'), '', cleansedName)
    cleansedName = re.sub(reOneInParens, '', cleansedName)
    #reFileExtention
    #logger.debug('clean: ' + cleansedName)
    return cleansedName
            

def moveToFolder() :
# do work with the duplicates
    logger.debug(str(len(allMovieFiles)) + " to " + targetMoveFolder)
    for file in allMovieFiles:
        fullPathFile = file[1]
        logger.debug(fullPathFile)
        af = eyed3.load(fullPathFile)
        print (af.tag.artist)
        
        newFolder = targetMoveFolder + af.tag.artist
        ArtistFolderExists = os.path.exists(newFolder)
        if ArtistFolderExists is False:
            logger.debug("make new folder: " + newFolder)
            os.mkdir(newFolder)
        shutil.move(fullPathFile, newFolder)


###############################################
##MAIN
#global vars
logger = prepLogger("musicToFolder")    
filehashes = dict()
duplicates = list()

logger.info("load a list of files")

for md in baseMusicDirs:
    all_files_from_path_gen(md)

moveToFolder()

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
