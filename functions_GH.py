from tweepy import OAuthHandler
from pymongo import MongoClient
import streaming
from tweepy import AppAuthHandler
from tweepy import API

# credentials to access your twitter application API
consumer_key = 'Insert Consumer Key here'
consumer_secret = 'Insert Consumer Secret here'
access_token = 'Insert Access Toker here'
access_token_secret = 'Inser Access Token Secret here'

# Initiating MongoDB database
client = MongoClient('localhost', 27017)  # Initiating MongoDB client, the MongoDB database service should be run from command prompt
clientTrain = MongoClient('localhost', 27018) # localhost is the server which is followed by the port number

def getauthentication(): # first way to get the authentication for twitter API
        auth = OAuthHandler(consumer_key, consumer_secret) #OAuth object
        auth.set_access_token(access_token, access_token_secret)
        return auth

def getapplevelauth(): # second way to get the twitter API authentication, it is known as App Level Authentication.
        auth = AppAuthHandler(consumer_key, consumer_secret)
        api = API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
        return api

def getdatabase(dbname, colname): # create a new database and a new collection in MongoDB, drop any existing data in the collection
        global client
        db = client[dbname]
        collection = db[colname]
        collection.remove({})
        return db, collection

def getdatabasenames(): # retrive all databases from the local MongoDB database server hosted in localhost
        global client
        dbs = client.database_names()        
        return dbs

def getcollectionnames(databasename): # retrive all collection names from a MongoDB database
        global client
        db = client[databasename]
        colls = db.collection_names()
        return colls

def savetodatabase(dbname,tocol,fromcol): # save a collection from fromcol to another collection named tocol
        db, coll = getdatabase(dbname, tocol)
        coll.insert(fromcol.find())

def search(keywords, timelimit): # the function initiates the twitter streaming API, and store them in a temporary database
        keywords = keywords.split()
        auth = getauthentication()
        db, collection = getdatabase('twitter_database', 'twitter_collection') # temporary database to hold the collected tweets
        count = streaming.streaming_tweet(auth, keywords, timelimit, collection) # call to the function that streams the tweets
        return count, collection


def searchTrain(keywords, timelimit): # will be called from classifier training module
        keywords = keywords.split()
        auth = getauthentication()
        #client = MongoClient('localhost', 27018)
        global clientTrain
        db = clientTrain['twitter_database']
        collection = db['twitter_collection']
        collection.remove({})
        count = streaming.streaming_tweet(auth, keywords, timelimit, collection) # call the function to stream the tweets
        return count, collection

def getdatabaseTrain(dbname, colname): # returning a database and collecting by its name. Creates a new one if it doesn't exist
        global clientTrain
        db = clientTrain[dbname]
        collection = db[colname]
        return db, collection

def getkeywords(): # if you want to take the keywords and timelimit as input from the user.
        x = str(input('Enter the keyword list seperated by white space:'))
        keywords = x.split()        
        timelimit = int(input('Enter the timelimit in Seceonds:'))
        print('Searching for keywords:'+str(keywords))
        print(' with a timelimt:'+str(timelimit))
        return [keywords, timelimit]
        
def savetodatabaseTrain(dbname,tocol,fromcol):
        db, coll = getdatabaseTrain(dbname, tocol)
        coll.insert(fromcol.find())

def getcollectionnamesTrain(databasename):
        global clientTrain
        db = clientTrain[databasename]
        colls = db.collection_names()
        return colls

def getdatabasenamesTrain():
        #client = MongoClient('localhost', 27018)
        global clientTrain
        dbs = clientTrain.database_names()        
        return dbs

def getexistingdb(dbname, colname):
        global client
        db = client[dbname]
        collection = db[colname]
        return collection
        
def getexistingdbTrain(dbname, colname):
        #client = MongoClient('localhost', 27018)
        global clientTrain
        db = clientTrain[dbname]
        collection = db[colname]
        return collection

def getexistingdbExpert(dbname, colname):
        #client = MongoClient('localhost', 27018)
        global clientTrain
        db = clientTrain[dbname]
        collection = db[colname]
        return db, collection

def getexistingdbTraindb(dbname):
        #client = MongoClient('localhost', 27018)
        global clientTrain
        db = clientTrain[dbname]
        return db
