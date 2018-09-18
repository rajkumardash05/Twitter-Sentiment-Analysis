import urllib.parse
import urllib.request
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
import simplejson
import functions_GH
from itertools import chain
import functools
import calendar
import time
import numpy as np
from collections import defaultdict
import nltk, string

# here several important functions will be defined


# an API that can be used to extract sentiment from tweet text
def tpdotcom(tweets):
        
        url = "http://text-processing.com/api/sentiment/" # website that provides the API
        opinions = {} # screen_name, sentiment pair

        for tweet in tweets:
                tweet_text = str(tweet.get('text'))
                
                # sentiment using text-processing.com API, has a limit of 1000 query per ip per day
                data = urllib.parse.urlencode({'text':tweet_text})
                data = data.encode('utf-8')
                u = urllib.request.urlopen(url, data)
                O = simplejson.loads(u.read())

                if opinions.get(tweet.get('user').get('screen_name')) == None: 
                        opinions[tweet.get('user').get('screen_name')] = [{tweet.get('id_str'):O}]
                else:
                        opinions[tweet.get('user').get('screen_name')]. append([{tweet.get('id_str'):O}])

                
        return opinions

def tpdotcomGUI(dbname, colname, coltweet): # when the function will be called from the dashboard

        opinions = functions.getexistingdb(dbname, colname) 
        tweet_collection = functions.getexistingdb(dbname, coltweet)
        tweets = tweet_collection.find()

        if opinions.count()==0: # opinion wasn't extracted from tweet text in any earlier time
                
                url = "http://text-processing.com/api/sentiment/"        

                for tweet in tweets:
                        if tweet.get('opinion_tpdotcom') == None:
                                tweet_text = str(tweet.get('text'))
                                
                                # sentiment using text-processing.com API, has a limit of 1000 query per ip per day
                                data = urllib.parse.urlencode({'text':tweet_text})
                                data = data.encode('utf-8')
                                u = urllib.request.urlopen(url, data)
                                O = simplejson.loads(u.read())
                                
                                opinions.insert(dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O]}))
                                tweet_collection.update({'id':tweet.get('id')}, {'$set':{'opinion_tpdotcom':O.get('probability').get('pos')}})                                



def textblobingNB(tweets): # a python library called text blob will be used to convert text to numeric sentiment, naivebayes classifier is used here
        db, opinions = functions.getdatabase('twitter_database', 'sentiment_collectionNB') # connected to the database

        for tweet in tweets:
                tweet_text = str(tweet.get('text'))
                O = TextBlob(tweet_text, analyzer=NaiveBayesAnalyzer()) # using naive Bayes 
                d = dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O.sentiment]})
                opinions.insert(dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O.sentiment]}))
                #print(d)
                
        return opinions

def textblobingNBGUI(dbname, colname, coltweet): # when the function will be called from the dashboard
        opinions = functions.getexistingdb(dbname, colname) # connected to the database
        tweet_collection = functions.getexistingdb(dbname, coltweet)
        tweets = tweet_collection.find()
        if opinions.count()==0:
                
                for tweet in tweets:
                        if tweet.get('opinion_tbnba') == None:                              
                                tweet_text = str(tweet.get('text'))                        
                                O = TextBlob(tweet_text, analyzer=NaiveBayesAnalyzer()) # using naive Bayes 
                                #d = dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O.sentiment]})
                                opinions.insert(dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O.sentiment]}))
                                tweet_collection.update({'id':tweet.get('id')}, {'$set':{'opinion_tbnba':O.sentiment[1]}})


def textblobingPA (tweets): # a python library called text blob with patern alalyzer class will be used to extract sentiment from tweet text
        db, opinions = functions.getdatabase('twitter_database', 'sentiment_collectionPA') # connected to the database

        for tweet in tweets:
                tweet_text = str(tweet.get('text'))
                O = TextBlob(tweet_text) # using patern analyzer
                d = dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O.sentiment]})
                opinions.insert(dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O.sentiment]}))
                #print(d)
                
        return opinions
        
        
def textblobingPAGUI(dbname, colname, coltweet): # when the function will be called from the dashboard
        opinions = functions.getexistingdb(dbname, colname) # connected to the database
        tweet_collection = functions.getexistingdb(dbname, coltweet)
        tweets = tweet_collection.find()
        #if opinions.count()==0:
        for tweet in tweets:
                if tweet.get('opinion_tbpa') is None:
                        print('here I am')
                        tweet_text = str(tweet.get('text'))
                        O = TextBlob(tweet_text) # using naive Bayes 
                        #d = dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O.sentiment]})
                        opinions.insert(dict({tweet.get('id_str'):[tweet.get('user').get('screen_name'),O.sentiment]}))
                        tweet_collection.update({'id':tweet.get('id')}, {'$set':{'opinion_tbpa':O.sentiment[0]}})

def tpdotcomText(tweet_text): # functions can be called for individual tweet text
        url = "http://text-processing.com/api/sentiment/"
        data = urllib.parse.urlencode({'text':tweet_text})
        data = data.encode('utf-8')
        u = urllib.request.urlopen(url, data)
        Opinion = simplejson.loads(u.read())
        return Opinion

def textblobingNBText(tweet_text):
        Opinion = TextBlob(tweet_text, analyzer=NaiveBayesAnalyzer()) # using naive Bayes                
        return Opinion

def textblobingPAText(tweet_text):
        Opinion = TextBlob(tweet_text) # using naive Bayes 
        return Opinion


def preprocessGUI(dbname, colname): # any preprocessing step can be added here for trimming tweet text to discard unnecessary text
        
        collection = functions.getexistingdb(dbname, colname)
        tweets = collection.find()
        for t_id, text, entries in ((t['id'],t['text'], t['entities']) for t in tweets):
                #print('before: '+text)
                urls = (e['url'] for e in entries['urls'])
                users = ('@'+e['screen_name'] for e in entries['user_mentions'])
                hashtags = ('#'+e['text'] for e in entries['hashtags'])
                text = functools.reduce(lambda t,s: t.replace(s, ''), chain(urls, users, hashtags), text) # removes all urls, usermentions and hashtags from the tweet text
                collection.update({'id':t_id}, {'$set':{'textP':text}})
                #print('after: '+text)

def profilingGUI(profilecol, dbname, colname): # generating the profile of a user by finding their friend and follower count, bio-information, verified status, listed count, tweets count
        collection = functions.getexistingdb(dbname, colname)
        tweets = collection.find()
        api = functions.getapplevelauth()

        for tweet in tweets:
                texts = []
                count = 0
                profile = {'screen_name': tweet.get('user').get('screen_name'),
                            'id': tweet.get('id'),
                            'friends_count': tweet.get('user').get('friends_count'),
                            'followers_count': tweet.get('user').get('followers_count'),
                            'description': tweet.get('user').get('description'),
                            'listed_count': tweet.get('user').get('listed_count'),
                            'verified': tweet.get('user').get('verified'),
                            'statuses_count':tweet.get('user').get('statuses_count')}

                user_tweets = api.user_timeline(screen_name = tweet.get('user').get('screen_name'), count = 200, include_rts = False)
                count += len(user_tweets)

                for ut in user_tweets:
                        texts.append([ut.get('text'),ut.get('retweet_count'), ut.get('retweeted'), ut.get('favourites_count')]) 
                oldest = user_tweets[-1].id

                while True:
                        user_tweets = api.user_timeline(screen_name = tweet.get('user').get('screen_name'), count = 200, include_rts = False, max_id=str(oldest-1))
                        count +=len(user_tweets)
                        if not user_tweets:
                                break
                        oldest = user_tweets[-1].id
                        for ut in user_tweets:
                                texts.append([ut.get('text'),ut.get('retweet_count'), ut.get('retweeted'), ut.get('favourites_count')])
                profile['tweet_texts'] = texts
                profile['tweet_count'] = count
                profilecol.insert(profile)

        return profilecol


def preprocessTrain(collection, tweet_id):
        tweet = collection.find_one({'id':tweet_id})
        text = tweet['text']
        urls = (e['url'] for e in tweet['entities']['urls'])
        users = ('@'+e['screen_name'] for e in tweet['entities']['user_mentions'])
        hashtags = ('#'+e['text'] for e in tweet['entities']['hashtags'])
        text = functools.reduce(lambda t,s: t.replace(s, ''), chain(urls, users, hashtags), text)
        collection.update({'id':tweet_id}, {'$set':{'text':text}})


def   collectweblinksTrain(dbname,sname,tweetcoll):
        collection_name = dbname+'_tweetstatus'
        coll = functions.getexistingdbTrain(dbname, collection_name)
        weblinks = {}
        tweets = tweetcoll.find()
        for tweet in tweets:
                weblinks.update({tweet.get('id_str'): {'urls':[e['url'] for e in tweet['entities']['urls']],'rt_count':tweet.get('retweet_count'),'fv_count':tweet.get('favourites_count')}})
        coll.insert(dict({'screen_name':sname,'weblinks':weblinks}))
        return weblinks

def collectweblinksExpert(tweetcoll): # for the timebeing weblinks are not saved anywhere
        weblinks={}
        tweets = tweetcoll.find()
        for tweet in tweets:
                weblinks.update({tweet.get('id_str'): {'urls':[e['url'] for e in tweet['entities']['urls']],'rt_count':tweet.get('retweet_count'),'fv_count':tweet.get('favourites_count')}})
        return weblinks
                                  
