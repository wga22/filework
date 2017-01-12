from twitter import *

#273213222-R9P8iHbGZnImsbW4glwuqzNS1Rg9h8swNCrymGDE
#l5lIaOE5dG3zYItTx91jkChSSl3iCaksUmd1daq2M7PgI
# api key eBcH12ELTJiTMfHRfkjgxlrwC  
# api secret jnwLwVoRbOIzekVhnvFNBVpEG4taNA1Kjgk6zL6pB8UBLAN9NE
# Authentication details. To  obtain these visit dev.twitter.com
#consumer_key = 'nWGEdfoaBt7d6wWhiAw5Tw'
#consumer_secret = 'qM4QfDPqG9JQp6n0fqTCMrj6LJjES6vu2IzqpZLc'
#access_token = '2284416938-JbD4F32m9xQPMxKoh6UikpCLoJm8F6xy8wDPS9P'
#access_token_secret = 'XvJZQWa6zz5vHcHkUcYBacQKZJE9pcxbpxUUgNo9rN4AG'

#273213222-R9P8iHbGZnImsbW4glwuqzNS1Rg9h8swNCrymGDE
#l5lIaOE5dG3zYItTx91jkChSSl3iCaksUmd1daq2M7PgI

consumer_key = 'eBcH12ELTJiTMfHRfkjgxlrwC'
consumer_secret = 'jnwLwVoRbOIzekVhnvFNBVpEG4taNA1Kjgk6zL6pB8UBLAN9NE'
access_token = '273213222-R9P8iHbGZnImsbW4glwuqzNS1Rg9h8swNCrymGDE'
access_token_secret = 'l5lIaOE5dG3zYItTx91jkChSSl3iCaksUmd1daq2M7PgI'


t = Twitter(
            auth=OAuth(access_token, access_token_secret,
                       consumer_key, consumer_secret)
           )


# see "Authentication" section below for tokens and keys

# Get your "home" timeline
t.statuses.home_timeline()

# Get a particular friend's timeline
t.statuses.user_timeline(screen_name="wga22")
