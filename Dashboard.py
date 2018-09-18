import tkinter as tk
import tkinter.ttk as ttk
import functions_GH
import sentimentanalysis_GH
import graphconstruction
#databasename = 'saved_database'

class mainwindow():
        def __init__(self, master):

                self.master = master
                self.frame = tk.Frame(self.master)
                self.keylbl = tk.Label(self.frame, text = 'Kewwords:')
                self.keyframe = tk.Frame(self.frame, width = 200, height = 20)
                self.timelbl = tk.Label(self.frame, text = 'Time:')
                self.timeent = tk.Entry(self.frame)
                self.searchbtn = tk.Button(self.frame, text = 'Search', state = 'disabled', command = self.search) # search button to initiate streaming.
                self.loadbtn = tk.Button(self.frame, text = 'Load', state = 'normal', command= self.load)
                self.mwposition()
                self.keyframe.columnconfigure(0, weight=10)
                self.keyframe.grid_propagate(False)
                self.keyent = tk.Entry(self.keyframe)
                self.keyent.grid(sticky='WE')
                self.keyent.bind('<Key>', lambda e:self.searchbtn.config(state='normal'))                
                self.app1=analysiswindow(self.master)

        def mwposition(self):
                
                self.keylbl.grid(column = 0, row = 0)
                self.keyframe.grid(column = 1, row = 0)
                self.timelbl.grid(column = 2, row = 0)
                self.timeent.grid(column = 3, row = 0)
                self.searchbtn.grid(column = 4, row = 0)
                self.loadbtn.grid(column=5, row=0, padx=5)
                self.frame.grid(column = 0, row = 0, columnspan=3, padx = 15)

        def search(self): # will initiate the streaming process from Twitter.com
                self.count = 0
                if self.keyent.get() == '':
                        self.showmsg('Please provide at least one keywords')
                else:                        
                        if self.timeent.get()=='':
                                self.count, self.coll = functions_GH.search(self.keyent.get(), 300) # default time for streaming is 300 seconds
                                self.showlistbox()
                                self.showmsg('The number of collected tweets is:'+str(self.count))
                        else:
                                self.count, self.coll = functions_GH.search(self.keyent.get(), int(self.timeent.get()))
                                self.showlistbox()
                                self.showmsg('The number of collected tweets is:'+str(self.count))                       

        def load(self): # loading a collection of previously collected tweets from MongoDB database

                self.coll = functions_GH.getexistingdb(self.app1.dbcombo.get(),self.app1.dbcombo.get()+'_tweets') # assumed that collection name was formed by concatenating _tweets after the database name
                self.showlistbox()
                self.showmsg('Loaded from the database named'+self.app1.dbcombo.get()+', '+self.app1.dbcombo.get()+'_tweets')

        def showmsg(self, msg):
                
                tk.messagebox.showinfo('info',msg)
                
        def showlistbox(self): # will produce a listbox showing all the twitter users in the current database

                self.lbframe = tk.Frame(self.master, width = 100, height = 50)
                self.snlistbox = tk.Listbox(self.lbframe)
                self.snlistbox.grid(column=0, row=0, sticky='N')                
                self.lbscrollbar = tk.Scrollbar(self.lbframe, orient = 'vertical', command=self.snlistbox.yview)
                self.lbscrollbar.grid(column=1, row=0, sticky='NS')
                self.snlistbox.config(yscrollcommand=self.lbscrollbar.set)
                self.lbframe.grid(column = 0, row = 1, sticky='NW')
                self.snlistbox.bind('<Double-1>', self.showsentiment)
                self.snlistbox.bind('<<ListboxSelect>>', self.showsentiment)
                self.savebutton = tk.Button(self.lbframe, text='Save',command=self.savetodatabase)
                self.savebutton.grid(column=0, row=1, padx=5,pady=5)
                
                tweets = self.coll.find()
                index = 0
                for tweet in tweets:
                        self.snlistbox.insert('end', tweet.get('user').get('screen_name'))
                        if index%2 == 0:
                                self.snlistbox.itemconfigure(index, background = '#f0f0ff')
                        index = index+1

        def showsentiment(self, *args): # will create a text box showing the tweet text, preprocessed tweet text if any, and the sentiment scores

                self.snmtcomboselected = tk.StringVar()
                self.chkbtnvar = tk.IntVar()
                self.snmtframe = tk.Frame(self.lbframe, width = 75, height = 50)
                self.snmtframe.grid(column=2,row=0,sticky='NWES')
                self.snmttext = tk.Text(self.snmtframe, width=75, height=25)
                self.snmttext.grid(column=0,row=0,sticky='N')
                idx = self.snlistbox.curselection()
                index = int(idx[0])

                self.selectedTweettext = self.coll.find_one({'user.screen_name':self.snlistbox.get(index)}).get('text') # getting the tweet text for the selected users in the user listbox
                self.snmttext.insert('end', self.selectedTweettext+'\n\n')
                
                self.selectedTweettextP = self.coll.find_one({'user.screen_name':self.snlistbox.get(index)}).get('textP') # getting the preprocessed text of the selected user's tweet
                if self.selectedTweettextP != None:
                        self.snmttext.insert('end', 'After Preprocessing: '+self.selectedTweettextP+'\n\n')
                
                self.opframe = tk.Frame(self.snmtframe, width=50, height = 25)
                self.opframe.grid(column=0,row=1,sticky='WS')
                self.polaritylbl = tk.Label(self.opframe, text='Polarity')
                self.subjectivitylbl = tk.Label(self.opframe, text='Neutrality')
                self.polaritylbl.grid(column=0,row=0)
                self.subjectivitylbl.grid(column=2,row=0)
                self.polarityentry = tk.Entry(self.opframe)
                self.subjectivityentry = tk.Entry(self.opframe)
                self.polarityentry.grid(row=0,column=1)
                self.subjectivityentry.grid(row=0,column=3)
                self.snmtcombo = ttk.Combobox(self.opframe, textvariable=self.snmtcomboselected, state = 'readonly')                
                self.snmtcombo['values']=('text-processing.com', 'textblob_NaiveBayesAnalyzer', 'textblob_PatterntAnalyzer')
                self.snmtcombo.current(0)
                self.showopinionfirsttime()
                self.snmtcombo.grid(column=4,row=0)
                self.snmtcombo.selection_clear()
                self.snmtcombo.bind('<<ComboboxSelected>>', self.showopinions)
                self.chkbtn=tk.Checkbutton(self.opframe, text='Preprocessed Text', variable= self.chkbtnvar)
                self.chkbtn.grid(column=5, row=0, sticky='E', padx=10)
                
                
        def showopinionfirsttime(self): 

                self.opinion = sentimentanalysis_GH.tpdotcomText(self.selectedTweettext)
                self.snmttext.insert('end', self.opinion)
                self.polarityentry.insert('0',self.opinion.get('probability').get('pos'))
                self.subjectivityentry.insert('0',self.opinion.get('probability').get('neutral'))
                #print(self.opinion.get('probability').get('pos'))

        def showopinions(self, *args):

                self.snmttext.delete('1.0', 'end')
                self.snmttext.insert('end', self.selectedTweettext+'\n')
                if self.selectedTweettextP != None:
                        self.snmttext.insert('end', self.selectedTweettextP+'\n')
                if self.chkbtnvar.get()==0:
                        self.text = self.selectedTweettext
                elif self.chkbtnvar.get()==1:
                        self.text=self.selectedTweettextP
                print('selected text:' + self.text)
                if self.snmtcombo.get() == 'text-processing.com':
                        self.opinion = sentimentanalysis_GH.tpdotcomText(self.text)
                        self.snmttext.insert('end', self.opinion)
                        self.subjectivitylbl['text'] = 'Neutrality'
                        self.polarityentry.delete('0','end')
                        self.subjectivityentry.delete('0','end')
                        self.polarityentry.insert('0',self.opinion.get('probability').get('pos'))
                        self.subjectivityentry.insert('0',self.opinion.get('probability').get('neutral'))                        
                elif self.snmtcombo.get() == 'textblob_NaiveBayesAnalyzer':
                        self.opinion = sentimentanalysis_GH.textblobingNBText(self.text)
                        self.snmttext.insert('end', self.opinion.sentiment)
                        self.polaritylbl['text'] = 'Positivity'
                        self.subjectivitylbl['text'] = 'Negativity'
                        self.polarityentry.delete('0','end')
                        self.subjectivityentry.delete('0','end')
                        self.polarityentry.insert('0',self.opinion.sentiment[1])
                        print(self.opinion.sentiment[1])
                        self.subjectivityentry.insert('0',self.opinion.sentiment[2])
                elif  self.snmtcombo.get() =='textblob_PatterntAnalyzer':
                        print('checkbtn:'+str(self.chkbtnvar.get()))
                        self.opinion = sentimentanalysis_GH.textblobingPAText(self.text)
                        self.snmttext.insert('end', self.opinion.sentiment)
                        self.subjectivitylbl['text'] = 'Subjectivity'
                        self.polarityentry.delete('0','end')
                        self.subjectivityentry.delete('0','end')
                        self.polarityentry.insert('0',self.opinion.sentiment[0])
                        self.subjectivityentry.insert('0',self.opinion.sentiment[1])

                else:
                        print('Cant Match')
                        
        def savetodatabase(self): # You can save the collected tweets in your own database by giving it a name, the collection name will be created automatically by adding _tweets at the end of the database name
                
                self.database=popupwindow(self.master, 'Database Name:')
                self.master.wait_window(self.database.getinput)
                print('databasename:'+self.database.dbname)
                functions_GH.savetodatabase(self.database.dbname,self.database.dbname+'_tweets',self.coll)
                self.app1.databases = functions_GH.getdatabasenames()
                self.app1.dbcombo['values']=self.app1.databases
                self.app1.dbcombo.current(0)
                
class analysiswindow():  # this class will compute all the necessary analysis.
        def __init__(self, master):

                global databasename
                self.dbcomboselected = tk.StringVar()
                self.analcomboselected = tk.StringVar()
                self.master = master
                self.spaceframe = tk.Frame(self.master,width=50)
                self.spaceframe.grid(row=0,column=3,columnspan=2,sticky='NSEW')
                self.frame = tk.Frame(self.master)
                self.frame.grid(row=0,column=5, pady=5, padx=5)

                self.dbcombo = ttk.Combobox(self.frame, textvariable=self.dbcomboselected, state = 'readonly')
                self.analcombo = ttk.Combobox(self.frame, textvariable=self.analcomboselected, state = 'readonly')
                self.databases = functions_GH.getdatabasenames()
                #self.collections.remove('system.indexes')
                self.dbcombo['values']=self.databases
                self.analcombo['values']=('text-processing.com', 'textblob_NaiveBayesAnalyzer', 'textblob_PatterntAnalyzer')
                if len(self.databases) != 0:
                        self.dbcombo.current(0)                
                self.analcombo.current(0)
                
                self.dbcombo.grid(column=0,row=0, columnspan=2, padx=5, pady=5)
                self.dbcombo.selection_clear()
                self.analcombo.grid(column=2,row=0, columnspan=2, padx=5, pady=5)
                self.analcombo.selection_clear()              
                self.dbcombo.bind('<<ComboboxSelected>>', self.buttonsetup)

                self.preprocessbtn = tk.Button(self.frame, text = 'Preprocess Tweets', command = self.preprocess)
                self.profilebtn = tk.Button(self.frame, text = 'Construct Profile', command = self.profiling)

                self.analysebtn = tk.Button(self.frame, text = 'Analyse Sentiment', command = self.analyse)
                self.generateGraphbtn = tk.Button(self.frame, text = 'Construct Graph', command = self.constructGraph)
                self.drawGraphbtn = tk.Button(self.frame, text = 'Draw Graph', state='disabled', command = self.drawGraph)               
                
                self.preprocessbtn.grid(row=1,column=0, padx=5, pady=5)
                self.profilebtn.grid(row=1,column=1, padx=5, pady=5)
                
                self.analysebtn.grid(row=2, column=0, padx=5, pady=5)
                self.generateGraphbtn.grid(row=2, column=1, padx=5, pady=5)
                self.drawGraphbtn.grid(row=2, column=2, padx=5, pady=5)

                                
        def buttonsetup(self, *args):
                
                self.drawGraphbtn.config(state='disabled')

        def preprocess(self): # applying some preprocessing step, that will remove the user mentions from the tweet text.

                print('In Preprocess')
                sentimentanalysis_GH.preprocessGUI(self.dbcombo.get(), self.dbcombo.get()+'_tweets') # this function will do this preprocessing and store the tweet text in the database after the processing

        def profiling(self): # generating the profile of a user by finding their friend and follower count, bio-information, verified status, listed count, tweets count
                print('In profiling')
                self.profilecollection = functions_GH.getexistingdb(self.dbcombo.get(), self.dbcombo.get()+'_profile')
                if self.profilecollection.count() == 0:
                        self.profilecollection = sentimentanalysis_GH.profilingGUI(self.profilecollection, self.dbcombo.get(), self.dbcombo.get()+'_tweets')
                        tk.messagebox.showinfo('info','Profile construction has been completed')
                else:
                        tk.messagebox.showinfo('info','Profile has been constructed previously')        

        def analyse(self): # this will compute the opinions for each of the tweets in the database and tag them with the tweets
                print('In Analysis')
                if self.analcombo.get() == 'text-processing.com':
                        sentimentanalysis_GH.tpdotcomGUI(self.dbcombo.get(),self.dbcombo.get()+'_tpdotcom', self.dbcombo.get()+'_tweets')

                elif self.analcombo.get() == 'textblob_NaiveBayesAnalyzer':
                        sentimentanalysis_GH.textblobingNBGUI(self.dbcombo.get(),self.dbcombo.get()+'_tbnba', self.dbcombo.get()+'_tweets')

                elif  self.analcombo.get() =='textblob_PatterntAnalyzer':
                        sentimentanalysis_GH.textblobingPAGUI(self.dbcombo.get(),self.dbcombo.get()+'_tbpa', self.dbcombo.get()+'_tweets')

                tk.messagebox.showinfo('info','Analysis Done')
                
                
        def constructGraph(self): # the underlying user graph will be constructed here
                #global databasename
                print('In Generate Graph')
                self.graphcollection = functions_GH.getexistingdb(self.dbcombo.get(), self.dbcombo.get()+'_graph')
                #print(self.graphcollection.count)
                if self.graphcollection.count()==0:
                        self.vertices, self.edges = graphconstruction.constructgraphAlternate(functions_GH.getexistingdb(self.dbcombo.get(), self.dbcombo.get()+'_tweets').find())                                
                        self.graphcollection.insert(dict({'vertices':self.vertices,'edges':self.edges}))
                        tk.messagebox.showinfo('info','Graph has been constructed and saved to database')
                else:
                        for graph in self.graphcollection.find():
                                self.vertices = graph.get('vertices')
                                self.edges = graph.get('edges')
                        tk.messagebox.showinfo('info','Graph retrived from database')
                self.drawGraphbtn.config(state='normal')
                self.graph = graphconstruction.networkxgraph(self.vertices, self.edges)

        def drawGraph(self): # the constructed graph will be drawn and displayed here
                print('In Draw Graph')
                graphconstruction.drawgraph(self.graph)
                

class popupwindow():
        def __init__(self, master, label):
                self.getinput = tk.Toplevel(master)
                self.lbl = tk.Label(self.getinput, text=label)
                self.lbl.pack()
                self.entry=tk.Entry(self.getinput)
                self.entry.pack()
                self.button = tk.Button(self.getinput, text='Ok', command=self.cleanup)
                self.button.pack()
        def cleanup(self):
                self.dbname = self.entry.get()
                self.getinput.destroy()

if __name__ == '__main__':
        root = tk.Tk()
        root.title('Twitter Opinion Mining')
        root.geometry('1200x600')
        app = mainwindow(root)
        #app1=analysiswindow(root)
        root.mainloop()
