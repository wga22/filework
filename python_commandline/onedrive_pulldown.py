import glob
import hashlib
import os
import shutil
import logging

#constants
photodirs = ["C:/Users/Will/SkyDrive/Pictures/MEMORIES"]
logfilePath = "d:/temp/"
targetFolder = "D:/temp/pics/"
clientid = '0000000048156469'
clientSecret = 'wsfL3R7t73jXYgJ5SeNQWJnYmOPLx1EC'



def prepLogger(appName):
	_logger = logging.getLogger(appName)
	hdlr = logging.FileHandler(logfilePath + "python_"+appName+"log.txt")
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	_logger.addHandler(hdlr) 
	_logger.addHandler(logging.StreamHandler())
	_logger.setLevel(logging.INFO)
	return _logger

