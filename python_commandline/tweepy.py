import tweepy



# Authentication details. To  obtain these visit dev.twitter.com
consumer_key = 'nWGEdfoaBt7d6wWhiAw5Tw'
consumer_secret = 'qM4QfDPqG9JQp6n0fqTCMrj6LJjES6vu2IzqpZLc'
access_token = '2284416938-JbD4F32m9xQPMxKoh6UikpCLoJm8F6xy8wDPS9P'
access_token_secret = 'XvJZQWa6zz5vHcHkUcYBacQKZJE9pcxbpxUUgNo9rN4AG'

if __name__ == '__main__':
    # Create authentication token
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    print ('Getting statistics for @BarackObama:')

    # Get information about the user
    data = api.get_user('BarackObama')

    print ('Followers: ' + str(data.followers_count))
    print ('Tweets: ' + str(data.statuses_count))
    print ('Favouries: ' + str(data.favourites_count))
    print ('Friends: ' + str(data.friends_count))
    print ('Appears on ' + str(data.listed_count) + ' lists')
