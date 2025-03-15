import tweepy



# Authentication details. To  obtain these visit dev.twitter.com
consumer_key = 'tt'
consumer_secret = 'tt'
access_token = 'tt-tt'
access_token_secret = 'tt'

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
