import glob
import hashlib
import os
import shutil
import logging
import re

#constants
#moviedirs = ["D:/video/family", "D:/video/movieseries", "D:/video/documentaries", "D:/video/unwatched", "D:/video/archivemovies"]
moviedirs = ["Z:/video"]
logfilePath = "d:/temp/"
allMovieFiles = []
targetMoveFolder = "D:/temp/delme/"
#reFileExtention = re.compile('\.{mkv|mp4|avi}')
reFileExtention = re.compile('\.(mkv|mp4|avi)')
#reYear= re.compile([\[|\(]\d\d\d\d\)|\])
reYear= re.compile( '[\[|\(]\d\d\d\d[\]|\)]' )
reThe = re.compile('^the ', re.IGNORECASE)
reCharOnly = re.compile('![a-z]')
#reFileExtention = re.compile('\.mkv')
#reFileExtention = re.compile('.*')

def prepLogger(appName):
	_logger = logging.getLogger(appName)
	hdlr = logging.FileHandler(logfilePath + "python_"+appName+"log.txt")
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	_logger.addHandler(hdlr) 
	_logger.addHandler(logging.StreamHandler())
	_logger.setLevel(logging.INFO)
	return _logger

#yield os.path.join(root, d, f)
def all_files_from_path_gen(p):
	print("all files: " + p)
	retfiles = []
	for root, dirs, files in os.walk(p):
		for d in dirs:
			logger.debug("add directory: " +d)
			#retfiles.extend(all_files_from_path_gen(root+d))
		for f in files:
			allMovieFiles.append([f, (root+"/"+f)])

def simpleMovieName(fileName):
	cleansedName = fileName.lower()
	cleansedName = re.sub(reThe, '', cleansedName)
	cleansedName = re.sub(reFileExtention, '', cleansedName)
	cleansedName = re.sub(reYear, '', cleansedName)
	cleansedName = re.sub(reCharOnly, '', cleansedName)
	cleansedName = re.sub(re.compile('\.'), '', cleansedName)
	cleansedName = re.sub(re.compile(' '), '', cleansedName)

	#reFileExtention
	logger.debug('clean: ' + cleansedName)
	return cleansedName
			
def findDupes():
	matchCount = 0
	for file_name in allMovieFiles:
		#logger.debug("file:" + file_name[0])
		#if re.search(reFileExtention, file_name[0]) is not None:
		if re.search(reFileExtention, file_name[0]) is not None:
			matchCount += 1
			filehash = simpleMovieName(file_name[0])
			if filehash in filehashes:
				logger.debug("collision! " + file_name[0] + "  == " + filehash)
				duplicates.append({"filepath":file_name[1], "hash": filehash, "original":file_name[0]})
				logger.info("DUPE: " + file_name[1])
			else:
				filehashes[filehash] = file_name[1]
				#logger.debug ('new file found hash: ' + filehash + " for filename: " + file_name[1])
	logger.info('%(hits)i / %(all)i files' % {'hits': matchCount ,'all':len(allMovieFiles)})

def moveDupes() :
# do work with the duplicates
	for x in duplicates:
		outputDetails = "D file: " + x["filepath"] + "\n original: " + x["original"]
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

for md in moviedirs:
	all_files_from_path_gen(md)

findDupes()

#moveDupes()

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
