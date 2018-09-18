import functions_GH
import tweepy
from more_itertools import unique_everseen
import networkx as net
import matplotlib.pyplot as plt
#from sentimentanalysis import cosine_sim
from collections import Counter

def constructgraph(tweets):
        verticesSN = []
        verticesUID = []
        edgesSN = []
        edgesUID = []
        usercollection = functions.getexistingdb('twitter_database', 'userinfo')
        auth = functions.getauthentication()
        api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
        
        for tweet in tweets:  # user names will be extracted from the tweet and be considered as the vertices for the graph
                verticesSN.append(tweet.get('user').get('screen_name')) # get the screen name as vertex identifier
                verticesUID.append(tweet.get('user').get('id')) # get the user id also
                verticesSN = list(unique_everseen(verticesSN)) # remove all the duplicate elements from the vertices
                verticesUID = list(unique_everseen(verticesUID)) # remove all the duplicate elements from the vertices        
        
        count = 0
        
        for usn in verticesSN:  # all followers of the current user pool will be extracted to generate the edges between two users
                count = count+1
                follower_ids = []

                try:
                        if usercollection.find_one({'screen_name':usn}) == None:
                                for page in tweepy.Cursor(api.followers_ids, screen_name = usn).pages():
                                        follower_ids.extend(page)
                                usercollection.insert_one({'screen_name':usn, 'followers_ids':follower_ids}) # generate the userinfo database                                                 
                        
                except tweepy.TweepError as error:
                        print (error)
 
                        if str(error) == 'Not authorized.':
                                print ('Can''t access user data - not authorized.')
                                continue
 
                        if str(error) == 'User has been suspended.':
                                print ('User suspended.')
                                continue

                        errorObj = error[0][0]
 
                        print (errorObj)
 
                        if errorObj['message'] == 'Rate limit exceeded':
                                print ('Rate limited. Sleeping for 15 minutes.')
                                time.sleep(15 * 60 + 15)
                                continue
                        continue
                except KeyboardInterrupt:
                        print('Visited user counts: '+str(count))
                        response = input()
                        if response == 'quit':
                                break
                        else:
                                continue

        for v1 in verticesSN:  # the edges will be constructed here
                for v2 in verticesSN:
                        followerlist = usercollection.find_one({'screen_name':v2}).get('followers_ids')
                
                        if verticesUID[verticesSN.index(v1)] in followerlist:
                                edgesSN.append((v2,v1))
                                edgesUID.append((verticesUID[verticesSN.index(v2)], verticesUID[verticesSN.index(v1)]))
                        
        return verticesSN, edgesSN

def constructgraphAlternate(tweets):
        verticesSN = []
        verticesUID = []
        edgesSN = []
        edgesUID = []
        usercollection = functions.getexistingdb('twitter_database', 'userinfo')
        auth = functions.getauthentication()
        api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
        
        for tweet in tweets:
                verticesSN.append(tweet.get('user').get('screen_name')) # get the screen name as vertex identifier
                verticesUID.append(tweet.get('user').get('id')) # get the user id also

        verticesSN_D = Counter(verticesSN) # SN and their count
        verticesSN = list(unique_everseen(verticesSN)) # remove all the duplicate elements from the vertices
        verticesUID = list(unique_everseen(verticesUID)) # remove all the duplicate elements from the vertices        

        #for uid in verticesUID:
        
        count = 0
        
        SNmorethanone = []
        verticesSNreturn = []
        SNmorethanoneUID = []
        
        for user in verticesSN_D:
                if verticesSN_D.get(user) > 1:
                        SNmorethanone.append(user) # list of user having more than one tweet
                        SNmorethanoneUID.append(verticesUID[verticesSN.index(user)])
        print(len(SNmorethanone))
        
        for usn in SNmorethanone:
                count = count+1
                print('Number of user visited: '+ str(count)+ ' now visiting '+ usn)
                follower_ids = []
                try:
                        if usercollection.find_one({'screen_name':usn}) == None:
                                print('getting user follower list for the first time for '+ usn)
                                for page in tweepy.Cursor(api.followers_ids, screen_name = usn).pages():
                                        if len(follower_ids) >= 25000:
                                                break
                                        follower_ids.extend(page)
                                usercollection.insert_one({'screen_name':usn, 'followers_ids':follower_ids}) # generate the userinfo database                                                 
                except tweepy.TweepError as error:
                        print (error)
                        usercollection.insert_one({'screen_name':usn, 'followers_ids':[]})
 
                        if str(error) == 'Not authorized.':
                                print ('Can''t access user data - not authorized.')
                                continue
 
                        if str(error) == 'User has been suspended.':
                                print ('User suspended.')
                                continue

                        continue
                except KeyboardInterrupt:
                        print('Visited user counts: '+str(count))
                        response = input()
                        if response == 'quit':
                                break
                        else:
                                continue

        verticesSNreturn.extend(SNmorethanone)

        for v2 in SNmorethanone: # edges will be constructed here
                followerlist = usercollection.find_one({'screen_name':v2}).get('followers_ids')
                for v1 in verticesSN:                                
                        if verticesUID[verticesSN.index(v1)] in followerlist:
                                edgesSN.append((v2,v1))
                                verticesSNreturn.append(v1)
                                edgesUID.append((SNmorethanoneUID[SNmorethanone.index(v2)], verticesUID[verticesSN.index(v1)]))                        
        verticesSNreturn = list(unique_everseen(verticesSNreturn))
        return verticesSNreturn, edgesSN


def networkxgraph(nodes, edges):
        graph = net.DiGraph() # empty graph object
        graph.add_nodes_from(nodes) # add the nodes
        graph.add_edges_from(edges) # add the edges
        return graph

def drawgraph(graph):
        pos = net.spring_layout(graph) # position layout of the nodes
        size = graph.number_of_nodes() # How many nodes in the final graph
        color = 'blue' # colors of the node
        transparency = 0.5  # transparency of the nodes
        plt.axis('off')

        net.draw_networkx_nodes(graph, pos, node_size = size, node_color = color, alpha = transparency)
        net.draw_networkx_edges(graph, pos, width = .8, alpha = transparency, edge_color = color)
        net.draw_networkx_labels(graph, pos, font_size = 12, font_family = 'sans-serif')
        #net.draw_networkx_edge_labels(graph, graph_pos = pos, edge_labels = labels_dict, pabel_pos = .3)
        plt.show() 
