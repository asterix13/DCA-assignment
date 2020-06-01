from tweepy import API 
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
 
import twitter_credentials
import numpy as np
import pandas as pd
import time

# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth

# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()    

    def stream_tweets(self, fetched_tweets_filename):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        hash_tag_list=['yes','no','hi']
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app() 
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords: 
        stream.filter(track=hash_tag_list)


# # # # TWITTER STREAM LISTENER # # # #
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True
          
    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """
    def countALLYES(self,df): # Counts all yes in the data-frame
        count=0
        for i in df['Tweets']:
            if 'yes' in i:
                count+=1
        return (count/len(df))
    def countSlidingYES(self,df,window=300):# Counts all yes in the last 300 tweets 
        count=0
        for i in df['Tweets'][(len(df)-window):len(df)]:
            if 'yes' in i:
                count+=1
        return (count/len(df))
    def countBufferNO(self,df):# Counts all no in the first 100 letters of tweets 
        count=0
        for i in df['Tweets']:
            if 'no' in i[0:100]:
                count+=1
        return (count/len(df))
    def countRandomHI(self,df):# counts number of random tweets with hi
        count=0
        i=0
        
        while i < len(df):
            if 'hi' in df['Tweets'][i]:# random sampling
                
                count+=1
            print(df['Tweets'][i])
            i+=int(time.time()%100)
        return count
    
    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['Tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['text'] = np.array([tweet.text for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df 
if __name__ == '__main__':

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()
    tweets = api.user_timeline(screen_name="realDonaldTrump", count=900)

    #print(dir(tweets[0]))
    #print(tweets[0].retweet_count)

    df = tweet_analyzer.tweets_to_data_frame(tweets)
    count=tweet_analyzer.countALLYES(df)    
    print("Counting all the 'yes's in recieved tweets= ",count*100,"%")
    count=tweet_analyzer.countSlidingYES(df)    
    print("Counting all the 'yes's in last 300 tweets= ",count*100,"%")
    count=tweet_analyzer.countBufferNO(df)    
    print("Counting all the 'no's in all tweets but searching only first hundred characters= ",count*100,"%")
    count=tweet_analyzer.countRandomHI(df)    
    print("Counting random 'hi's per hundred tweets= ",count," number of 'hi's")
    
