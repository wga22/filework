import tweepy
user = tweepy.get_user('twitter')
public_tweets = tweepy.api.public_timeline()
for tweet in public_tweets:
    print (tweet.text)