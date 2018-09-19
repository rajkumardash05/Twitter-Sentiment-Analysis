'''
1. This program is used to predict a twitter user's subsequent opinions from her initial opinion. To do so, I used an implementation of my paper published in ICONIP 2015.
2. This paper mainly analysed the impact of neighbours (friends) and external sources (mainly news media) opinions on an user's own opinion
3. For prediction, an user's first opinion in our dataset is considered her initial opinions, then using her neighbours' and external sources opinions, her subsequent opinions
   are predicted. Finally, the predicted and her original subsequent opinions were depicted as an outcome. The algorithm was stablised with some state-of-the arts papers
4. This program was written to use twitter data from MongoDB, however, to make a running version, an extract (with some modifications) of the dataset for subset of users
   was stored as json format and subsequently read from there.
5. Functions from the original version that use data from MongoDB was also kept as it is. However, instructions related to MongoDB is commented out.
'''
import functions_GH
import sentimentanalysis_GH
from collections import Counter
from more_itertools import unique_everseen
import numpy as np
import math
import random
import matplotlib.pyplot as plt
import calendar
import time
import tweepy
import json

''' Following code with comments read necessary data from MongoDB.
Three collections for (i) collected twitters, (ii) collected user details, and (iii) collected neighbour information
'''
#database_name = 'twitter_database'   # databse name
#collection_name = 'twitter_collection' # tweets collection
#collection_name_userinfo = 'twitter_userinfo' # collection for user information
#collection_name_userneighingo = 'userinfo_neighbour' # collection for neighbour information

#tweetscollection = functions_GH.getexistingdbTrain(database_name, collection_name) # getting the tweet collections
#usercollection = functions_GH.getexistingdbTrain(database_name, collection_name_userinfo) # getting the collected information from the tweet database
#userfncollection = functions_GH.getexistingdbTrain(database_name, collection_name_userneighingo)


''' The following code will read the data extract from corresponding json files to run this program. '''
# getting tweets of five extracted users.
with open('tweets.json', 'r') as fp:
    tweets_dict = json.load(fp)
tweets_dict = json.loads(tweets_dict)

# getting user specific information
with open('users.json', 'r') as fp:
    data = json.load(fp)

data = json.loads(data)
users = {}
for d in data:
        users.update(d)

# getting neighbour list of the users
with open('neighbour.json', 'r') as fp: 
    neigh_dict = json.load(fp)
neigh_dict = json.loads(neigh_dict)

# getting neighbours' tweets. Note not all details of neighbours' tweet were saved in the file. Only necessary ones to run this code are there
with open('neighbour_tweets.json', 'r') as fp:
    ntweets_dict = json.load(fp)
ntweets_dict = json.loads(ntweets_dict)


verticesUID = users.get('ids') # MongoDB version: verticesUID = usercollection.find_one({'user_ids':'user_ids'}).get('ids') # unique users in the collected database

# retrive the users information (who have original tweet interleaved with link/retweets)
user_sns = users.get('users_SN') # users' screen names
user_ids = users.get('users_ID') # users' twitter ID
user_tc = users.get('users_TC') # users' tweet count in our database
user_otc = users.get('users_OTC') # users' original tweet count, tweet that authored by the users excluding re-tweet or tweet with website links
user_otd = users.get('users_OTD') # 
user_steps = users.get('users_STEPS')

filename = "Stats_Vaccination.txt" # file to save some stats for further comparative analysis

auth = functions_GH.getauthentication()
api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

print('total unique users in the database {}'.format(len(verticesUID)))

def entropy(labels): # function to compute Shannon entropy for the opinion prediction algorithm
        datapoints = np.array(labels)*10 # multiply each element by 10 to convert it into binary values
        datapoints = np.floor(datapoints) # convert to corresponding integer values
        hist = np.bincount(datapoints.astype(int), minlength = 10)
        
        n_labels = len(labels)
        probs = hist / n_labels        

        n_classes = np.count_nonzero(probs)        
        if n_classes <= 1:
                return [0,0]
        ent = 0.
        enp = 0.
        
        for i in range(len(probs)):
                if probs[i] != 0:
                        ent -= probs[i] * math.log10(probs[i])
                        enp += probs[i]*((i/10)+.05)
        
        return [ent, enp]

def get_tweets(user_id):  # extract the individual tweets that were stored in the json file
        user_tweets = []

        for tweet in tweets_dict:
                if tweet.get('user').get('id') == user_id:
                        user_tweets.append(tweet)
        return sorted(user_tweets, key=lambda k: k['id'])

def get_ntweets(user_id): # extract individual neighbour's tweets from the saved json file, json files were read earlier
        n_tweets = []

        for tweet in ntweets_dict:
                if tweet.get('user_id') == user_id:
                        n_tweets.append(tweet)
        return sorted(n_tweets, key=lambda k: k['id'])

def get_neighbours(user_id): # extract neighbours of individual users
        for nei in neigh_dict:
                if nei.get('user_id_neighbours') == user_id:
                        return nei.get('neighbours_ids')

def get_neighbours_mongo(user_id): # extracting neighbours of individual users if they were saved in MongoDB, not used in this version
        friends_ids = []
        neighbours = []
        
        if userfncollection.find_one({'user_id_neighbours':user_id}) == None:
                print('First time neighbour collection')
                if userfncollection.find_one({'user_id_friend':user_id}) == None:
                        print('first time in friend collection')
                        try:
                                for page in tweepy.Cursor(api.friends_ids, user_id = user_id).pages():
                                        if len(friends_ids) >= 25000:
                                                break
                                        friends_ids.extend(page)
                                userfncollection.insert_one({'user_id_friend':user_id, 'friends_ids':friends_ids}) # generate the userinfo database

                        except:
                                print('an error occured')
                else:
                        print('directly in friend collection')
                        friends_ids.extend(userfncollection.find_one({'user_id_friend':user_id}).get('friends_ids'))                        
                        
                for friend in friends_ids:
                        if friend in verticesUID:
                                neighbours.append(friend) # neighbours are recognised by their ids
                                
                userfncollection.insert_one({'user_id_neighbours':user_id, 'neighbours_ids':neighbours}) # generate the userinfo database
        else:
                print('Neighbours are already computed')
                neighbours = userfncollection.find_one({'user_id_neighbours':user_id}).get('neighbours_ids') 

        return neighbours


def print_graph(op_ini, op_runs, user): # to generate the graph showing the prediction accuracy
        print('in print graph function for {}'.format(user))
        x_points = []
        avg = np.zeros(len(op_ini))
        for i in range(len(op_ini)):
                x_points.append(i)                                       
        plt.plot(x_points, op_ini, 'bo--',marker='o',label = 'Tweets_Op')
        for i in range(len(op_runs)):                
                avg = avg+np.array(op_runs[i])
        avg = avg/len(op_runs)
        plt.plot(x_points, avg.tolist(),'g^-', marker = '^', label = 'Sim_op')
        plt.title('Opinion Formation')
        plt.xlabel('Iteration Numbers')
        plt.ylabel('User Opinions')
        plt.legend(bbox_to_anchor=(.75, 1), loc=2, borderaxespad=0.)
        axes = plt.gca()
        axes.set_ylim([0,1.1])
        plt.savefig('figures/'+user+'.png', bbox_inches='tight')
        plt.clf()        
        return avg

def ES_validation():

        for user_id in user_ids: # iterate using user id through those who have at least two original tweets seperated by original tweets
                                        
                pncount = [] # participating neighbour count
                pntcount = []
                pEScount = []
                                
                run = 10
                results = []

                opinions_ini = [] # initial opinions of the user
                creation_time = [] # creation time of the tweets
                ot_position = []

                
                #tweets = tweetscollection.find({'user.id':user_id}).sort('id',1) # MongoDB version of extracting tweets.
                tweets = get_tweets(user_id)
                
                print('Simulating for the user {} having a total original tweets {} and steps count {} and total tweets of {}'.format(user_sns[user_ids.index(user_id)], user_otc[user_ids.index(user_id)], user_steps[user_ids.index(user_id)], len(tweets)))

                # simulation parameters initialization
                pos = 0
                tweet_distribution = user_otd[user_ids.index(user_id)]

                pES_OPS = []
                participating_ES = [] # which external sources are going to participate in this iteration                
                pES_OP = []      # opinion of these tweets
                pos = np.nonzero(np.array(tweet_distribution)==1)
                start = pos[0][0] # start position of original tweet: first original tweet position
                end = pos[0][-1]+1 # end position of original tweet: last original tweet position

                for i in range(start,end): # going through the tweet distribution of a user                                                        

                        if tweet_distribution[i] == 1: # for an  original tweet
                                tweet = tweets[i] # get the contents of the original tweets
                                creation_time.append(tweet.get('created_at')) # creation time of the original tweets                                
                                
                                op = tweet.get('Sentiment')
                                if op == None:
                                        op = sentimentanalysis_GH.textblobingNBText(tweet.get('text')).sentiment[1] # get the sentiment of the tweet
                                        tweetscollection.update_one({'id':tweet.get('id')},{'$set':{'Sentiment':op}})
                                
                                print('Original tweet at position {} havin opinion {}'.format(i,op))
                                opinions_ini.append(op) # original tweets are forming the initial opinion set of the agent
                                print('Participating ES Op {} and count {}'.format(pES_OP, len(participating_ES)))
                                pES_OPS.append(pES_OP) # participating tweets for this original tweet
                                pEScount.append(len(participating_ES))
                                
                                participating_ES = [] # preparing for collecting ES for next original tweets
                                pES_OP = []      # opinion of these tweets

                        elif tweet_distribution[i] == 0: # tweets having links for generating external sources' opinions                                             
                                tw = tweets[i]                                
                                ESTID = tw.get('id')
                                participating_ES.append(ESTID) # this tweet has the participating ES
                                if tw.get('Sentiment') == None:# 
                                        Opinion = sentimentanalysis_GH.textblobingNBText(tw.get('text')).sentiment[1]
                                        tweetscollection.update_one({'id':ESTID},{'$set':{'Sentiment':Opinion}})                                        
                                        pES_OP.append(Opinion)
                                else:                                
                                        pES_OP.append(tw.get('Sentiment'))
                                
                print('Own opinion and ES opinion generation Completed')
                with open(filename, 'a') as wfp:
                        wfp.write('User Screen Name: '+ str(user_sns[user_ids.index(user_id)])+'\n')
                        wfp.write('Total original tweets: '+ str(user_otc[user_ids.index(user_id)])+'\n')
                        wfp.write('Total tweets: '+ str(len(tweets))+'\n')
                        wfp.write('Total steps: '+str(user_steps[user_ids.index(user_id)])+'\n')
                        wfp.write('Original tweet Opinions: '+ str(opinions_ini)+'\n')                
                                
                neighbours = get_neighbours(user_id) # collecting the neighbours of this user
                
                pneigh_tweetOPS = []                                
                for i in range(len(opinions_ini)-1): # for each of the opinions, we are simulating
                                
                        tweet_time_a = calendar.timegm(time.strptime(creation_time[i], "%a %b %d %H:%M:%S +0000 %Y"))
                        tweet_time_b = calendar.timegm(time.strptime(creation_time[i+1], "%a %b %d %H:%M:%S +0000 %Y"))
                                
                        participating_neigh = [] # which neighbours are going to participate in this iteration
                        pneigh_tweetID = []      # what are the tweets that are participating in this iteration
                        pneigh_tweetOP = []      # opinion of these tweets                                                

                        for neigh in neighbours: # collecting neighbours' opinions for this iteration
                                tweetN = get_ntweets(neigh)  #MongoDB version: tweetscollection.find({'user.id':neigh}) # all tweets of a particular user
                                for t in tweetN:   
                                        tweet_timeN = calendar.timegm(time.strptime(t.get('created_at'), "%a %b %d %H:%M:%S +0000 %Y"))                                        
                                        if tweet_timeN >= tweet_time_a and tweet_timeN < tweet_time_b:
                                                participating_neigh.append(neigh) # found a participating neighbour
                                                neighTID = t.get('id') # the id of that tweet
                                                pneigh_tweetID.append(neighTID)
                                                        
                                                if t.get('Sentiment') == None: 
                                                        Opinion = sentimentanalysis_GH.textblobingNBText(t.get('text')).sentiment[1]
                                                        #tweetscollection.update_one({'id':neighTID},{'$set':{'Sentiment':Opinion}})                        
                                                        pneigh_tweetOP.append(Opinion) 
                                                else:                                                        
                                                        pneigh_tweetOP.append(t.get('Sentiment'))                                                                                

                        pntcount.append(len(participating_neigh)) # how many participating neighbours tweets
                        pneigh_tweetOPS.append(pneigh_tweetOP) # participating neighbours for all the iterations are saved
                        pncount.append(len(list(unique_everseen(participating_neigh)))) # participating neighbours' count                                                                       

                print('Neighbour opinion generation Completed')
                        
                print('Neighbours count: {}'.format(len(neighbours)))

                update_rules_combined = [0]*8 # Update rule statistics


                # Opinion predictor algorithm
                for r in range(run): # the number of runs  
                        print('***************** Run %d **********************', r)                        

                        opinion_up = [opinions_ini[0]] # updated opinion populated with the initial opinion
                        update_rule = [-1]
                        opinion_WA = 0 # weighted average of the user's opinions
                        direction_WA = 0
                        sign_t = 1
                        sign_tm1 = 1
                        for i in range(len(opinions_ini)-1): # for each of the opinions, we are simulating
                                if (i+1) < 4: # window size for weighted average computation is 4, i starts with zero but we already have one data
                                        alpha = 2/(i+2) # alpha = 2/(N+1)
                                else:
                                        alpha = 0.4                                

                                print('Participating ES: {} and Participating Neighbour tweet: {}'.format(pEScount[i+1], pntcount[i]))
                                
                                opinion_WA = opinion_up[i]*alpha + (1-alpha)*opinion_WA
                                if sign_t == sign_tm1:
                                        direction_C = 1
                                else:
                                        direction_C = 0
                                        
                                direction_WA = alpha*direction_C + (1-alpha)*direction_WA
                                distance_OP = abs(opinion_up[i]-opinion_WA)
                                x_O = float(direction_WA/(distance_OP+direction_WA))
                                a_O = float(math.log10(1+x_O)/math.log10(1+1))
                                
                                if (pntcount[i]) != 0: # this iteration has a participating neighbour. size(OT array) = size(pntcount) + 1     
                                        pneigh_tweetOP = pneigh_tweetOPS[i]
                                        en_ON = 1 - (entropy(pneigh_tweetOP)[0]/math.log10(10)) # opinion consistency
                                        avg_ON = np.mean(pneigh_tweetOP)
                                        d_ON = abs(opinion_up[i]-avg_ON)
                                        x_ON = float(en_ON/(d_ON+en_ON))
                                        print('x_ON {}'.format(x_ON))
                                        a_ON = float(math.log10(1+x_ON)/math.log10(1+1))
                                else:
                                        a_ON = 0
                                        
                                if (pEScount[i+1]) != 0: # has participating ES, initial OT also has its ES values. size(OT array) = size(pEScount)                                        
                                        pES_OP = pES_OPS[i+1]
                                        print('This iteration have participating ES {}'.format(len(pES_OP)))
                                        en_OES = 1 - (entropy(pES_OP)[0]/math.log10(10)) # opinion consistency
                                        avg_OES = np.mean(pES_OP)
                                        d_OES = abs(opinion_up[i]-avg_OES)
                                        x_OES = float(en_OES/(d_OES+en_OES))
                                        print('x_OES {}'.format(x_OES))
                                        a_OES = float(math.log10(1+x_OES)/math.log10(1+1))
                                else:
                                        a_OES = 0
                                        
                                if (pntcount[i]) == 0 and (pEScount[i+1]) == 0:                                        
                                        opinion_up.append(opinion_up[i])
                                        update_rule.append(-1) # no participating neighbours
                                        sign_tm1 = sign_t
                                        sign_t = 1                                        
                                else:
                                        a_high = 0.75
                                        a_low = 0.25
                                        success = 0

                                        if a_ON >= a_low and a_OES >= a_low:
                                                if a_ON >= a_high or a_OES >= a_high:
                                                        opinion_up.append(float((a_O*opinion_up[i]+a_ON*avg_ON+a_OES*avg_OES)/(a_O+a_ON+a_OES)))
                                                        update_rule.append(1)                                                                                                
                                                        success = 1
                                                else:
                                                        p_OP = pneigh_tweetOP+pES_OP # all the tweets in a set
                                                        d = []
                                                        for op in p_OP:
                                                                d.append(abs(opinion_up[i]-op))
                                                        p_OP = [x for (y,x) in sorted(zip(d,p_OP), reverse=False)]
                                                        d = sorted(d, key=float, reverse=False )
                                                        prob = random.random()

                                                        for k in range(len(p_OP)):
                                                                if prob <= (1-d[k]):
                                                                        opinion_up.append(float((a_O*opinion_up[i]+(1-d[k])*p_OP[k])/(a_O+(1-d[k]))))
                                                                        update_rule.append(2)
                                                                        success = 1
                                                                        break
                                        elif a_ON >= a_low and a_OES < a_low: 
                                                prob = random.random()
                                                if prob <= a_ON:
                                                        opinion_up.append(float((a_O*opinion_up[i]+a_ON*avg_ON)/(a_O+a_ON)))
                                                        update_rule.append(3)                                                
                                                        success = 1
                                                else:
                                                        d = []
                                                        for op in pneigh_tweetOP:
                                                                d.append(abs(opinion_up[i]-op))
                                                        p_ON = [x for (y,x) in sorted(zip(d,pneigh_tweetOP), reverse=False)]
                                                        d = sorted(d, key=float, reverse=False )
                                                        prob = random.random()

                                                        for k in range(len(p_ON)):
                                                                if prob <= (1-d[k]):
                                                                        opinion_up.append(float((a_O*opinion_up[i]+(1-d[k])*p_ON[k])/(a_O+(1-d[k]))))
                                                                        update_rule.append(4)
                                                                        success = 1
                                                                        break                                                
                                        elif a_ON < a_low and a_OES >= a_low:                                                
                                                prob = random.random()
                                                if prob <= a_OES:
                                                        opinion_up.append(float((a_O*opinion_up[i]+a_OES*avg_OES)/(a_O+a_OES)))
                                                        update_rule.append(5) 
                                                        success = 1
                                                else:
                                                        d = []
                                                        for op in pES_OP:
                                                                d.append(abs(opinion_up[i]-op))
                                                        p_OES = [x for (y,x) in sorted(zip(d,pES_OP), reverse=False)]
                                                        d = sorted(d, key=float, reverse=False )
                                                        prob = random.random()

                                                        for k in range(len(p_OES)):
                                                                if prob <= (1-d[k]):
                                                                        opinion_up.append(float((a_O*opinion_up[i]+(1-d[k])*p_OES[k])/(a_O+(1-d[k]))))
                                                                        update_rule.append(6)
                                                                        success = 1
                                                                        break                                                                                                                                        
                                        if success == 0:
                                                        opinion_up.append(opinion_up[i])
                                                        update_rule.append(0)                                               
                                        if i == 1: # after the first iteration, not enough data for sign change
                                                sign_t = np.sign(opinion_up[-1]-opinion_up[-2]) # data for sign change is the last two iterations
                                                sign_tm1 = sign_t
                                        else:
                                                sign_tm1 = sign_t
                                                sign_t = np.sign(opinion_up[-1]-opinion_up[-2])
                                                                                
                        print('Update Rules: {}'.format(update_rule))                        
                        results.append(opinion_up)
                        for rule in update_rule:
                                if rule == -1:
                                        update_rules_combined[7] = update_rules_combined[7]+1
                                else:
                                        update_rules_combined[rule] = update_rules_combined[rule] + 1
                
                avg = print_graph(opinions_ini, results, user_sns[user_ids.index(user_id)])

                for i in range(len(update_rules_combined)):
                        update_rules_combined[i] = update_rules_combined[i]/10

                with open(filename, 'a') as wfp:                
                        wfp.write('Final Opinions: '+ str(avg.tolist())+'\n')
                        wfp.write('Update Rules Stat: '+str(update_rules_combined)+'\n')
                        wfp.write('Participating Neighbours count: '+ str(pncount)+'\n')
                        wfp.write('Participating Tweets count: '+ str(pntcount)+'\n')
                        wfp.write('Participating ES OP count: '+ str(pEScount)+'\n')
                        wfp.write('Neighbours: '+ str(len(list(unique_everseen(neighbours)))) +'\n\n\n')
                print('Initial Opinion: {}'.format(opinions_ini))
                print('Converged Opinion: {}'.format(avg.tolist()))


while(1):
        way = int(input('Our Approach (1) or exit(0): '))
        if way == 1:
                ES_validation()        
        elif way == 0:
                sys.exit(0)
        else:
                print('Invalid_Input')
                continue
