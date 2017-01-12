from twitter import *


t = Twitter(
            auth=UserPassAuth('will.allen@gmail.com', 'd@nielle')
           )
t.statuses.friends_timeline()
#t.search.tweets(q="#pycon")
		   
# see "Authentication" section below for tokens and keys

# Get your "home" timeline
#t.statuses.home_timeline()

#t.search.tweets(q="#pycon")