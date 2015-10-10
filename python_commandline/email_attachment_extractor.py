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
prefix= "B"
emaildirs = ["E:/gmail/"]
logfilePath = "d:/temp/"
targetFilePath = "d:/temp/pics_from_emails"
# not used targetMoveFolder = "D:/temp/pics_from_emails/"
counter = 1
imageRE = re.compile('image\/(\S+)')
validfilenameRE = re.compile('[\/\\:\*\?\"\<\>\|]') # \ / : * ? " < > |

def prepLogger(appName):
	_logger = logging.getLogger(appName)
	hdlr = logging.FileHandler(logfilePath + "python_"+appName+"log.txt")
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	# write to file
	_logger.addHandler(hdlr) 
	# write to screen
	_logger.addHandler(logging.StreamHandler())
	_logger.setLevel(logging.INFO)
	return _logger



#yield os.path.join(root, d, f)
def all_files_from_path_gen(p):
	logger.debug("all files: " + p)
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

def md5ChecksumFromFile(file):
	m = hashlib.md5()
	while True:
		data = file.read(8192)
		if not data:
			break
		m.update(data)
	return m.hexdigest()	
		
def getEmailFromFile(filePath):
#    with open(filePath, 'rb') as fh:
	msg = None
	try:
		f = open(filePath)
		msg = email.message_from_file(f)
		f.close()
	except:
		logger.error("failed to open file:" + filePath)
	return msg

		
def addDirectoryofPhotos(dirPath):
	#imagefiles = glob.glob(dirPath)
	imagefiles = all_files_from_path_gen(dirPath)
	#print(dirPath +" size: " + str(len(imagefiles)))
    #print path
	#for file_name in imagefiles:
	for file_name in imagefiles:
		filehash = md5Checksum(file_name)
		logger.debug ('hash: ' + filehash)
		if filehash in filehashes:
			logger.info("collision! " + file_name + "  -- " + filehash)
			duplicates.append({"filepath":file_name, "hash": filehash, "original":filehashes[filehash]})
			#logger.debug("move: " + file_name)
		else:
			filehashes[filehash] = file_name

def getmailaddresses(msg, name):
    """retrieve From:, To: and Cc: addresses"""
    addrs=email.utils.getaddresses(msg.get_all(name, []))
    for i, (name, addr) in enumerate(addrs):
        if not name and addr:
            # only one string! Is it the address or is it the name ?
            # use the same for both and see later
            name=addr
            
        try:
            # address must be ascii only
            addr=addr.encode('ascii')
        except UnicodeError:
            addr=''
        else:
            # address must match adress regex
            if not email_address_re.match(addr):
                addr=''
        addrs[i]=(getmailheader(name), addr)
    return addrs
			
def getImageAttachmentsFromEmail(eml, _counter):
	#TODO: prefix the file with the person the email is from (and subject?)
	#
	from_=getmailaddresses(eml, 'from')
	crash;
	for part in eml.walk():
		#logger.debug(eml.get("header") +" " +part.get_content_type())
		# multipart/* are just containers
		#logger.debug(" content type: " + part.get_content_type())
		m = imageRE.match(part.get_content_type())
		if part.get_content_maintype() == 'multipart' or not m:
			logger.debug("skipping: " + part.get_content_type())
			continue
		# Applications should really sanitize the given filename so that an
		# email message can't be used to overwrite important files
		
		#work out the file name
		filename = part.get_filename()
		if not filename:
			#work out the extension
			ext =  mimetypes.guess_extension(part.get_content_type())
			if not ext:
				ext = ("."+m.group(1))
			filename = 'unknown'+ext

		#filename = part.get_filename()+ '-%03d%s' % (_counter, ext)
		filename = prefix + str(_counter) + "_" + filename
		filename = re.sub(validfilenameRE, '_', filename)
		logger.debug("writing a file: "+ filename)
		#logger.debug("writing a file: " + part.get_content_type() + "  -> " + filename)
		_counter += 1
		try:
			with open(os.path.join(targetFilePath, filename), 'wb') as fp:
				fp.write(part.get_payload(decode=True))
				logger.debug(filename + " was written")
		except OSError as err:
			logger.error("ERROR: OS error: " + err)
	return _counter

#global vars
logger = prepLogger("email_attachment")	
logger.info("Pull all images from emails in a directory")

emailfiles = all_files_from_path_gen(emaildirs[0])

for eml_path in emailfiles:
	logger.debug("working with the email: " + eml_path)
	eml = getEmailFromFile(eml_path)
	if eml != None:
		counter = getImageAttachmentsFromEmail(eml, counter)
	else:
		logger.warn("this is not an email: " + eml_path)

logger.info("there were " + str(counter) + " files written")
	#break
#	email.message_from_file(eml)

	
'''
#for path in all_files_from_path_gen('C:/Users/Danielle/Pictures/'):
#    print (path)
for dr in photodirs:
	addDirectoryofPhotos(dr)

#addDirectoryofPhotos("C:/Users/Danielle/Pictures/prophotographer/*.jpg")
logger.info("size of hashes file:" + str(len(filehashes)))

# do work with the duplicates
for x in duplicates:
	outputDetails = "D file: " + x["filepath"] + "\n original: " + x["original"]
	print(outputDetails)
	logger.info(outputDetails)
	try:
		shutil.move(x["filepath"], targetMoveFolder)
	except (IOError) as why:
		logger.error(x["filepath"] + " already exists in target, removing instead")
		#os.remove(x["filepath"])




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
