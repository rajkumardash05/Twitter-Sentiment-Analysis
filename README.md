# Twitter-Sentiment-Analysis
Stream Twitter.com on a particular topic to collect tweets in real-time and analyse their sentiments to assess the overall sentiment of Twitter users on that topic. 

Raj: I am creating this repository to combine my python programs that were used to collect tweets from Twitter.com in real-time using it's Streaming API and then save them in MongoDB database, which will be then preprocessed to extract the tweet text and feed into a sentiment analysis program to find out the overall sentiment of Twitter users on a topic at a particular time.

Instructions:
opinionpredictor.py can predict a twitter user's opinions. To run this program, you need to read the json files that hold an extract from the original dataset used for simulation. The json files contain necessary data for doing the opinion prediction simulation for five users.

Dashboard.py creates a tkinter based GUI to initiate streaming from Twitter.com using a space separated list of keywords for a certain user-defined time. The dataset can be saved for subsequent use. From this dashboard, one can be able to see the user lists and tweets for individual users. Sentiments will be extracted based on several methods (can be selected from a drop-down menu). 

From the analyse panel of this dashboard, one can initiate preprocessing of the tweets by removing unnecessary elements from tweet text, can create a user profile database for the involved users, and can construct and display the underlying social network graph of the users.

To run dashboard.py, one has to create a Twitter App and need to copy the credentials from the App into functions_GH.py file. Moreover, the codes assume that there is a mongodb database service installed and run in the localhost. MongoDB_command.txt list the commands to run this service from windows command prompt.

A screenshot of the dashboard is also found in dashboard.jpg file.

Finally, sentimentanalyzer.py is a pilot example that can be run to stream twitter.com for a time period and compute the average sentiment of twitter users on that topic for that time period. No need of MongoDB to store the tweets, only need twitter Apps credentials. For testing, you can run with a keyword and 20 sec timelimit.
