import re
import glob
import hashlib
import os
import shutil
import logging
import email
import mimetypes
import sys
import email, mimetypes
from email.header import decode_header
#from email.Utils import parseaddr
#from email.Header import decode_header
# purpose is to pull all attachments off a set of EML files
#http://blog.magiksys.net/parsing-email-using-python-content

#constants
#emaildirs = ["D:/personalbackup/email/gmail"]
# prefix is the prefix to the outgoing file names to avoid naming collisions
testprefix= ""

'''
backup log
	pdf files from gmails
		2008_05-2011_10
		3/26/3015 - 8/23/3015
		
'''

emaildirs = ["E:/gmail/"]
#emaildirs = ["D:/temp/testemails/"]
#emaildirs = ["D:/personalbackup/email/gmail/"]
#emaildirs = ["E:/"]
logfilePath = "d:/temp/"
#targetFilePath = "d:/temp/pics_from_emails"
targetFilePath = "d:/temp/full_gmail_attachment_dump"



# not used targetMoveFolder = "D:/temp/pics_from_emails/"
counter = 0
#imageRE = re.compile('image\/(\S+)')
pdfRE = re.compile('pdf', re.I)
filetypeRE = re.compile('\S+\/(\S+)')
validfilenameRE = re.compile('[\/\\:\*\?\"\<\>\|,\r\n]') # \ / : * ? " < > |
#invalidWindowsFileCharRE = re.compile('[\/\\:\*\?\"\<\>\|]') # \ / : * ? " < > |
#validWinFileRE = re.compile('[^\\/:*?"<>|\r\n]*')
#EMAIL_ADDRESS_RE = re.compile('([a-z]|[A-Z]|[0-9])+@([a-z]|[A-Z]|[0-9])')
EMAIL_ADDRESS_RE = re.compile('.*')
#invalid_chars_in_filename='<>:"/\\|?*\%\''+reduce(lambda x,y:x+chr(y), range(32), '')
invalid_windows_name='CON PRN AUX NUL COM1 COM2 COM3 COM4 COM5 COM6 COM7 COM8 COM9 LPT1 LPT2 LPT3 LPT4 LPT5 LPT6 LPT7 LPT8 LPT9'.split()

atom_rfc2822=r"[a-zA-Z0-9_!#\$\%&'*+/=?\^`{}~|\-]+"
atom_posfix_restricted=r"[a-zA-Z0-9_#\$&'*+/=?\^`{}~|\-]+" # without '!' and '%'
atom=atom_rfc2822
dot_atom=atom  +  r"(?:\."  +  atom  +  ")*"
quoted=r'"(?:\\[^\r\n]|[^\\"])*"'
local="(?:"  +  dot_atom  +  "|"  +  quoted  +  ")"
domain_lit=r"\[(?:\\\S|[\x21-\x5a\x5e-\x7e])*\]"
domain="(?:"  +  dot_atom  +  "|"  +  domain_lit  +  ")"
addr_spec=local  +  "\@"  +  domain

email_address_re=re.compile('^'+addr_spec+'$')

class Attachment:
    def __init__(self, part, filename=None, type=None, payload=None, charset=None, content_id=None, description=None, disposition=None, sanitized_filename=None, is_body=None):
        self.part=part          # original python part
        self.filename=filename  # filename in unicode (if any) 
        self.type=type          # the mime-type
        self.payload=payload    # the MIME decoded content 
        self.charset=charset    # the charset (if any) 
        self.description=description    # if any 
        self.disposition=disposition    # 'inline', 'attachment' or None
        self.sanitized_filename=sanitized_filename # cleanup your filename here (TODO)  
        self.is_body=is_body        # usually in (None, 'text/plain' or 'text/html')
        self.content_id=content_id  # if any
        if self.content_id:
            # strip '<>' to ease searche and replace in "root" content (TODO) 
            if self.content_id.startswith('<') and self.content_id.endswith('>'):
                self.content_id=self.content_id[1:-1]

def prepLogger(appName):
	_logger = logging.getLogger(appName)
	hdlr = logging.FileHandler(logfilePath + "python_"+appName+"log.txt")
	formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
	hdlr.setFormatter(formatter)
	# write to file
	_logger.addHandler(hdlr) 
	# write to screen
	_logger.addHandler(logging.StreamHandler())
	_logger.setLevel(logging.DEBUG)
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
#	with open(filePath, 'rb') as fh:
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

			
def getmailheader(header_text, default="ascii"):
	"""Decode header_text if needed"""
	try:
		headers=decode_header(header_text)
	except email.errors.HeaderParseError:
		# This already append in email.base64mime.decode()
		# instead return a sanitized ascii string
		return header_text.encode('ascii', 'replace').decode('ascii')
	else:
		for i, (text, charset) in enumerate(headers):
			try:
				#headers[i]=unicode(text, charset or default,errors='replace')
				headers[i]=text
			except LookupError:
				# if the charset is unknown, force default
				headers[i]=text
		return u"".join(headers)
			
def getmailaddresses(msg, field2):
	"""retrieve From:, To: and Cc: addresses"""
	addrs=email.utils.getaddresses(msg.get_all(field2, []))
	outAddrs = []
	for i, (name, addr) in enumerate(addrs):
		logger.debug('getmailaddresses: field2: ' +field2 + " name:" + name + ' address: ' + addr)
		#logger.debug('zzzzz ' + name + ' = ' + addr)
		outAddrs.append({'name': name, 'address': addr, 'type': field2})
	return outAddrs
			
def getAllAttachmentsFromEmail(eml, _counter):
	from_eml_l =getmailaddresses(eml, "from")
	from_eml = 'UNK'
	if len(from_eml_l)>0:
		from_eml = from_eml_l[0].get('address')
	logger.debug("from address: " + from_eml)
	for part in eml.walk():
		#logger.debug(eml.get("header") +" " +part.get_content_type())
		# multipart/* are just containers
		#logger.debug(" content type: " + part.get_content_type())
		isPDFFile = pdfRE.search(part.get_content_type())
		if part.get_content_maintype() == 'multipart' or not isPDFFile:
			logger.debug("skipping: " + part.get_content_type())
			continue
		# Applications should really sanitize the given filename so that an
		# email message can't be used to overwrite important files
		
		#work out the file name
		filename = part.get_filename()
		ext =  mimetypes.guess_extension(part.get_content_type())
		if not ext:
			ext = ".pdf"

		if not filename:
			#work out the extension
			filename = "unknown"+ext

		
		#filename = part.get_filename()+ '-%03d%s' % (_counter, ext)
		#filename = from_eml +'_'+ str(_counter) + "_" + filename  # include the counter to make sure name is unique
		filename = from_eml + "_" + filename  # no counter, just overwrite same file name?
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
		except:
			logger.error("ERROR: general error: ")
	return _counter

def getImageAttachmentsFromEmail(eml, _counter):
	from_eml_l =getmailaddresses(eml, "from")
	from_eml = 'UNK'
	if len(from_eml_l)>0:
		from_eml = from_eml_l[0].get('address')
	logger.debug("from address: " + from_eml)
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
				ext = 'UNK'
			filename = 'unknown'+ext

		#filename = part.get_filename()+ '-%03d%s' % (_counter, ext)
		filename = from_eml +'_'+ str(_counter) + "_" + filename
		filename = re.sub(validfilenameRE, '_', filename)
		logger.debug("writing a file: "+ filename)
		#logger.debug("writing a file: " + part.get_content_type() + "  -> " + filename)
		try:
			with open(os.path.join(targetFilePath, filename), 'wb') as fp:
				fp.write(part.get_payload(decode=True))
				logger.debug(filename + " was written")
			_counter += 1
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
		counter = getAllAttachmentsFromEmail(eml, counter)
	else:
		logger.warn("this is not an email: " + eml_path)

logger.info("there were " + str(counter) + " files written")
	#break
#	email.message_from_file(eml)

	
'''
#for path in all_files_from_path_gen('C:/Users/Danielle/Pictures/'):
#	print (path)
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
	print '	------' + file_name

	with open(file_name) as f:
		for line in f:
			print '	' + line.rstrip()

	print

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
			#TODO: keeps breaking with byte error
			#logger.debug("Address?: " + addr)
			#if not EMAIL_ADDRESS_RE.match(addr):
			#	addr=''
			#addr='unk'		#due to todo, hard coding blank
			#addrs[i]=(getmailheader(name), addr)
			z=0

	
	'''
