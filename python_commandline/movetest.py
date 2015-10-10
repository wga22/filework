#import shutil
#shutil.move("D:/temp/Ala_Carte.pdf", "d:/temp/zz/")

import re
import glob
import hashlib
import os
import shutil
import logging
import email
import mimetypes

# purpose is to pull all attachments off a set of EML files

#constants
#emaildirs = ["D:/personalbackup/email/gmail"]
# prefix is the prefix to the outgoing file names to avoid naming collisions
prefix= "A"
emaildirs = ["E:/"]
logfilePath = "d:/temp/"
targetFilePath = "d:/temp/pics_from_emails"
# not used targetMoveFolder = "D:/temp/pics_from_emails/"
counter = 1
imageRE = re.compile('image\/(\S+)')
validfilenameRE = re.compile('[\/\\:\*\?\"\<\>\|]') # \ / : * ? " < > |

filename = re.sub(validfilenameRE, 'X', "\" > <801_=?ISO-8859-1?Q?YOUR_EMAIL_ACCOUNT_WON_(=A3550,000.00)_POUNDS.jpg")

print(filename)

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