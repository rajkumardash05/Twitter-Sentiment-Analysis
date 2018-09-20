import streaming
from tweepy import OAuthHandler
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

consumer_key = 'enter consumer key here'
consumer_secret = 'enter consumer secret here'
access_token = 'enter access token here'
access_token_secret = 'enter access token secret here'

Opinion = [0.0, 0.0]
start = 0

auth = OAuthHandler(consumer_key, consumer_secret) #OAuth object
auth.set_access_token(access_token, access_token_secret)

def compute_Sentiment(count, collection):
        global start
        Opinion[0] = 0.0
        for tweet in collection:
                tweet_text = str(tweet.get('text'))
                O = TextBlob(tweet_text, analyzer=NaiveBayesAnalyzer()) # using naive Bayes 
                Opinion[0] = Opinion[0] + O.sentiment[1]

        Opinion[0] = Opinion[0]/count

        if start == 0:
                Opinion[1] = Opinion[0]
                start = 1
        else:
                Opinion[1] = Opinion[0]*0.8+Opinion[1]*0.2                
                
if __name__ == '__main__':

        keywords = str(input('Search keywords seperated by space: '))
        timelimit = int(input('Time frequency to show the updated sentiments: '))

        while(1):
                count, collection = streaming.streaming_tweet_noDB(auth, keywords.split(), timelimit)        
                compute_Sentiment(count, collection)

                print('Current episode sentiment is: {} and average sentiment is: {}'.format(Opinion[0], Opinion[1]))
                action = int(input('Another episode (yes = 1, no = 0, change parameters = 2): '))
                if action == 1:                        
                        continue
                elif action == 2:
                        start = 0
                        keywords = str(input('Search keywords seperated by space: '))
                        timelimit = int(input('Time frequency to show the updated sentiments: '))                
                else:
                        break
