import gdata.docs.service
from xml.etree import ElementTree
# Create a client class which will make HTTP requests with Google Docs server.
client = gdata.docs.service.DocsService()
# Authenticate using your Google Docs email address and password.
client.ClientLogin('will.allen@gmail.com', 'PASSSSS')

# Query the server for an Atom feed containing a list of your documents.
documents_feed = client.GetDocumentListFeed()
# Loop through the feed and extract each document entry.
for document_entry in documents_feed.entry:
	# Display the title of the document on the command line.
	print (document_entry.title.text)
