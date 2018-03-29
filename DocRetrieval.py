"""    
 DocRetrieval.py

 This is a document indexing and retrieval
 system for Mark Hepple's Text Processing module,
 Fall 2013, University of Sheffield
 Author: Kelly Ogilvie. Assignment 1, COM 4115
 
 Your command-line options are as follows:
     -h Print this documentation string
     -s specify a stoplist (file name)
     -k remove (some) punctuation from the query
     -c specify a collection of documents to work with (file name)
     -b boolean query (string)
     -r ranked query (string)
     -x query file (file name)
     -q ranked query from query set (string ID number)
     -a batch process queries from the query set
     -n specify the number of results to return for a batch query
     -I create a new index 
     -i specify the index storage file (file name)
        note: for the -I and -i options, if you specify that you 
        would like a new index created, it will be stored in the filename 
        provided in -i, otherwise the index stored in -i will be loaded

"""

import sys, re, getopt, numpy as np
#PorterStemmer

# Set up command line options using getopt
opts, args = getopt.getopt(sys.argv[1:],'phkIs:b:i:c:r:q:ax:n:')
opts = dict(opts)

###HELP###
#If the help option is specified at the 
#command line, print the docstring and exit
if '-h' in opts:
    print __doc__
    sys.exit()


###STOPLIST###
#If a stoplist is specified in the command line,
#pre-process it for use later during indexing.
#An empty set is created whether a stoplist
#is specified or not.
stopset = set()
if '-s' in opts:
    stp = open(opts['-s'], 'r')
    for line in stp: 
        strippedline = line.strip()#necessary to strip linebreaks
        stopset.add(strippedline)
    stp.close()

###Top N results####
#allows user to specify
#the number of results to return for ranked queries
#default= 15
numResults = 15
if '-n' in opts:
    numResults = int(opts['-n'])


###COLLECTION###
#If a collection is specified in the command line,
#use it. Otherwise the default collection will be used.
collectionFile = 'documents.txt'
if '-c' in opts:
    collectionFile = opts['-c']
    
###QUERY FILE###
#If a query file is specified in the command line,
#use it. Otherwise the default query file will be used.
queryFile = 'queries.txt'
if '-x' in opts:
    queryFile = opts['-x']


charList = ['.', ',',  '?', '!', ';', ':', ')', '(',]
def removePunctuation(word):
    for char in charList:
        word = word.strip(char)
    return word 

######################

#Indexing

########


###NEW INDEX###
#If a new index is specified in the command line,
#perform indexing and save the index to the file specified 
#in the command line, or else the default index.txt
indexFile = 'index.txt'
docCount = 0
if '-I' in opts:
    tokenRe = re.compile(r'\w+')
    tokenCountDict = {}
    f = open(collectionFile, 'r')
    sectionRe = re.compile(r'(<document docid=)([0-9]+)(>)(.*?)(<\/document>)', re.DOTALL)
    m = sectionRe.findall(f.read())
    for str in m:
        docid = str[1]  
        text = str[3] 
        n = tokenRe.findall(text)
        for wd in n:
            wd = wd.lower()
            if wd not in stopset:
                if wd not in tokenCountDict:
                    tokenCountDict[wd] = {}
                if docid in tokenCountDict[wd]:
                    tokenCountDict[wd][docid] += 1
                else:
                    tokenCountDict[wd][docid] = 1
    ##write index to file in Brill format
    index = open(indexFile,'w')
    for wd in tokenCountDict:
        printstring = wd + " "
        for tag in tokenCountDict[wd]:
            printstring = printstring + '%s:%d' % (tag,tokenCountDict[wd][tag]) + " "
        index.write(printstring + "\n")
    index.close()
    print "Index created from documents."

###LOAD INDEX###
#load the index into a dictionary from the file
#specified in the command line or from the default
#index.txt

if '-I' not in opts: #**NOTE: may just end up making this default 'else' action
    #but make sure this happens before any queries get processed, or else make it a 
    #function 
    indexRe = re.compile(r'(\w+)')
    f = open('index.txt', 'r')
    tokenCountDict = {}
    for line in f:
        m = indexRe.findall(line)
        wd = m[0]
        docid = m[1::2]
        count = m[2::2]
        tokenCountDict[wd] = dict(zip(docid, count))
    print "Index loaded."


###COMPUTE REQUIRED VALUES###
#given a dictionary of words, their doc id's, and 
#their counts, compute the required values for use 
#in Retrieval calculations.

###Total number of documents in collection, |D|
docCount = 0
if '-c' in opts:
    f = open(opts['-c'], 'r')
else:
    f = open('documents.txt', 'r')
tokenRe = re.compile(r'\w+')
f = open(collectionFile, 'r')
sectionRe = re.compile(r'(<document docid=)([0-9]+)(>)(.*?)(<\/document>)', re.DOTALL)
m = sectionRe.findall(f.read())
for str in m:
   docCount += 1
#print docCount

###Number of documents containing each term, df_w, df[wd][0]
###inverse doc frequency log(|D|/df_w), df[wd][1]
df = {}
for wd in tokenCountDict:
    numDocs_w = 0
    idf = 0
    for doc in tokenCountDict[wd]:
        numDocs_w += 1
    idf = np.log10(docCount/numDocs_w)
    df[wd] = numDocs_w, idf
###Tf.IDF term weighting tf_wd * idf_wD 
###document vector sqrt(sum(tf_idf^2))
tf_idf = {}
docVector = {}
for wd in tokenCountDict:
    tf_idf[wd] = {}
    for doc in tokenCountDict[wd]:
        if doc not in docVector:
            docVector[doc] = 0
        idfi = df[wd][1]
        tfwd = tokenCountDict[wd][doc]
        tf_idf[wd][doc] = (float(idfi) * int(tfwd))
        docVector[doc] = docVector[doc] + tf_idf[wd][doc]**2
for doc in docVector:
    docVector[doc] = np.sqrt(docVector[doc])    

    
###########################
# SEARCHING
#
###################

###BOOLEAN QUERY###
#if a query was specified in the command line (-b)
#run a query on the string specified.

if '-b' in opts:
    #preprocess the query against the stoplist 
    #and search for query terms in the index.
    #store the sets of documents in the query dictionary.
    queryDocsDict = {}
    print "processing boolean query."
    query = opts['-b'] 
    queryList = query.split()
    for q in queryList:
        q = q.lower()
        if q not in stopset:
            if q in tokenCountDict:
                queryDocsDict[q] = set(tokenCountDict[q])  
    #create a single set which represents
    #the intersection of all the document sets
    #from the query dictionary.
    updatedSet = set()
    for r in queryDocsDict:
        if len(updatedSet) != 0:
            updatedSet = queryDocsDict[r].intersection(updatedSet)
            #print updatedSet
        else: 
            updatedSet = queryDocsDict[r]  
            #print updatedSet
    print "Processing Complete. Matching documents: "
    for doc in updatedSet:
        print doc

###############################################################
#Processing Queries and Performing Ranked Retrieval
###############################################################

        
#######Format a query when given a query ID#####
#takes a query ID entered at the command line 
#and finds it in the query file
#then saves it as a string.
def formatQueryByID(ID):
    regex = '(docid=' + ID + '>)(.+?)(</document)'
    idRE = re.compile(regex, re.DOTALL)
    f = open('queries.txt', 'r')
    m = idRE.search(f.read())
    if m:
        formatted = m.group(2)
        return formatted.strip()
    else: print "ID not found"
    


######Process a ranked query######
##### takes a query string and 
##### returns a dictionary of 
##### similarity calculations
def processQuery(query):
    queryCountDict = {}
    queryDocsDict = {}
    queryDocsCountDict = {}
    #save the query into a list 
    #and then process against the stopset.
    #depending on command line opts,
    #may remove punctuation 
    queryList = query.split()
    if '-k' in opts:
        #remove punctuation
        for i in range(len(queryList)):
            queryList[i] = removePunctuation(queryList[i])
            #print queryList
    #print queryList
    for q in queryList:
        q = q.lower()
        if q not in queryCountDict:
            queryCountDict[q] = 0
        queryCountDict[q] += 1
        if q not in stopset:
            if q in tokenCountDict:
                queryDocsDict[q] = set(tokenCountDict[q])
                queryDocsCountDict[q] = tokenCountDict[q]
                for doc in tokenCountDict[q]:
                    queryDocsCountDict[q][doc] = tokenCountDict[q][doc]
    #create a single set which represents
    #the union of all the document sets
    #from the query dictionary.
    unionSet = set()
    for r in queryDocsDict:
        if len(unionSet) != 0:
            unionSet = queryDocsDict[r].union(unionSet)
        else: 
            unionSet = queryDocsDict[r]  
     
      
    ##compute values for the query 
    
    ##calculate the query vector 
    #for each word in query:
        #first, look up the idf in df[wd][1]
        #then, look up tf in queryCountDict[wd]
        #square the idf*tf and add to the query vector
    #take the square root of the query vector value. this is the final query vector.

    queryVector = 0
    tf_idfQuery = {}
    for wd in queryDocsDict:
        #tf here is from the count of the term in the query, and the idf is from
        #the df[wd][1]
        if wd not in tf_idfQuery:
            tf_idfQuery[wd] = {}
        idf = df[wd][1]
        tf = queryCountDict[wd]
        tf_idfQuery[wd] = (float(idf) * int(tf))
        queryVector = queryVector + (tf*idf)
    queryVector = np.sqrt(queryVector)
    
    
    #####similarity calculation
    #using sum(queryweight*docweight) for each doc in matching set
    #divided by docvector
    simDict = {}
    for doc in unionSet:
        simDict[doc] = 0
        for wd in queryDocsDict:
            if doc in tf_idf[wd]: 
                simDict[doc] += (tf_idfQuery[wd] * tf_idf[wd][doc])
        simDict[doc] = simDict[doc]/docVector[doc]
    return simDict
    

###RANKED QUERY###
#if a ranked query was specified in the command line (-q)
#run a query on the string specified.

if '-r' in opts:
    queryString = opts['-r']
    #process the query
    print "processing query."
    results = processQuery(queryString)
   
    print "Top", numResults, "matches:"
    
    #now print the top N results, sorted by rank:
    docs = results.keys()
    docs.sort(reverse=True, key=lambda d:results[d])
    for i in range(numResults):
        print docs[i]#docs in order of rank



######Ranked Query from query set###
#if -q is specified at the command line
#run a query on the id provided


if '-q' in opts:

    queryID = opts['-q']
    #preprocess the file to find and strip the query
    queryString = formatQueryByID(queryID) 
        
    #process the query
    print "processing query."
    results = processQuery(queryString)
   
    print "Top", numResults, "matches:"
    
    #now print the top N results, sorted by rank:
    docs = results.keys()
    docs.sort(reverse=True, key=lambda d:results[d])
    for i in range(numResults):
        print docs[i]#docs in order of rank
   
####BATCH PROCESS QUERIES####
#batch processes queries from the file specified and 
#saves results to a results file   
#default is return top 15 results, but 
#a number may be specified in -n at the command line
if '-a' in opts:
    queryFile = 'queries.txt'
    if '-x' in opts:
        queryFile = opts['-x']
    IDList = []
    #access the file and create a list of ID numbers
    f = open(queryFile, 'r')
    idRE = re.compile(r'(docid=)(.+?)(>)', re.DOTALL)
    m = idRE.findall(f.read())
    for str in m:
        IDList.append(str[1]) 
    #print IDList
    #open the output file for writing results
    out = open('results.txt','w')
    for ID in IDList:      
    ##preprocess the file to find and strip the query
        queryString = formatQueryByID(ID) 
       
        #process the query
        print "processing query."
        results = processQuery(queryString)
        #append the results to results.txt file
        docs = results.keys()
        docs.sort(reverse=True, key=lambda d:results[d])
        #print docs
        #print ID
        for i in range(numResults):
            printstring = ID + " " + docs[i]
            print>> out, printstring
        print "results copied to file for ID: " + ID
    out.close()
  
