import glob
import hashlib
import os
import shutil
import logging

#constants
photodirs = ["C:/Users/Will/SkyDrive/Pictures/MEMORIES", "C:/Users/Will/Pictures/Memories 1","d:/temp/pics_from_emails","d:/temp/full_gmail_attachment_dump"]
#photodirs = ["d:/temp/pics_from_emails"]
logfilePath = "d:/temp/"
targetMoveFolder = "D:/temp/dupe_pics/"

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
			retfiles.append(root+"/"+f)
	return retfiles

def md5Checksum(filePath):
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()	

def addDirectoryofPhotos(dirPath):
	#imagefiles = glob.glob(dirPath)
	imagefiles = all_files_from_path_gen(dirPath)
	#print(dirPath +" size: " + str(len(imagefiles)))
    #print path
	#for file_name in imagefiles:
	for file_name in imagefiles:
		filehash = md5Checksum(file_name)
		if filehash in filehashes:
			logger.info("collision! " + file_name + "  -- " + filehash)
			duplicates.append({"filepath":file_name, "hash": filehash, "original":filehashes[filehash]})
			logger.info("move: " + file_name)
		else:
			filehashes[filehash] = file_name
			logger.debug ('new file found hash: ' + filehash + " for filename: " + file_name)




#global vars
logger = prepLogger("dupeFile")	
filehashes = dict()
duplicates = list()

logger.info("load a list of files")
logger.info("create md5 for each file")


#for path in all_files_from_path_gen('C:/Users/Danielle/Pictures/'):
#    print (path)
for dr in photodirs:
	addDirectoryofPhotos(dr)

#addDirectoryofPhotos("C:/Users/Danielle/Pictures/prophotographer/*.jpg")
logger.info("size of hashes file:" + str(len(filehashes)))

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
'''
