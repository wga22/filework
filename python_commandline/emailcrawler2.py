# -*- coding: utf-8 -*- 
import sys
import requests
import re

# In this example we're trying to collect e-mail addresses from a website

# Basic e-mail regexp:
# letter/number/dot/comma @ letter/number/dot/comma . letter/number
email_re = re.compile(r'([\w\.,]+@[\w\.,]+\.\w+)')

# HTML <a> regexp
# Matches href="" attribute
link_re = re.compile(r'href="(.*?)"')

def crawl(url, maxlevel):
    # Limit the recursion, we're not downloading the whole Internet
    if(maxlevel == 0):
        return

    # Get the webpage

    req = 32
    try: 
        req = requests.get(url)
    except:
        print("issue with URL:" + url)
    
    result = []

    # Check if successful
    if(req.status_code != 200):
        return []

    # Find and follow all the links
    links = link_re.findall(req.text)
    for link in links:
        # Get an absolute URL for a link
        # will link = urlparse.urljoin(url, link)
        try:
            result += crawl(link, maxlevel - 1)
        except:
            print("issue:" + link)
    # Find all emails on current page
    result += email_re.findall(req.text)
    return result

emails = crawl('http://unc.edu/about/contact-us/', 2)

print( "Scrapped e-mail addresses:")
for e in emails:
    print(e)
