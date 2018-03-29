 DocRetrieval.py

 This is a document indexing and retrieval
 system for Mark Hepple's Text Processing module,
 Fall 2013.  
 Author: Kelly Ogilvie. Assignment 1, COM 4115
 
***************
QUICK START:
***************
To execute batch queries with a stoplist (and create a new index at the same time) use the following configuration at the command line:

%run DocRetrieval.py -s stop_list.txt -a queries.txt -I

to evaluate the results, use:

%run eval_ir.py cacm_gold_std.txt results.txt

*You must include the following files in the same directory:

documents.txt
eval_ir.py
cacm_gold_std.txt
stop_list.txt


***************
***************

In This File:

	[1.] Help
	[2.] Stoplist
	[3.] Simple Boolean Retrieval
	[4.] Ranked Retrieval
	[5.] Retrieving for the full query set
	[6.] Additional configuration options, 
		including indexing
	

[1.] Help
To print the help documentation included in DocRetrieval.py, use the -h option.

[2.] Stoplist
To use a stoplist, use -s followed by the stoplist filename. There is no default stoplist, so if no stoplist is specified, no stoplist will be used.

Please note that both the index and the queries are processed with a stoplist if one is specified. This means that you will need to be aware of whether a stoplist was used when you originally created the index (using -I) and recreate the index if one is needed.

[3.] Simple Boolean Retrieval
To perform a simple Boolean retrieval, use -b followed by a query string. A list of document IDs for all matching documents will be displayed in the console window.

[4.] Ranked Retrieval
For single ranked queries, use -r followed by a query string. For queries from a query file, use -q followed by a query ID. Please note that the default query file is queries.txt, unless another file is specified using -x.

[5.] Retrieving for the full query set
TO batch process the full query set, use -a. You can specify a filename using -x, otherwise the default file 'queries.txt' will be used. This process will write the results to 'results.txt' in a format that can be used by the eval_ir.py program.

[6.] Additional configuration options
To create a new index, use the -I option. To specify the index file name, use -i followed by a filename, otherwise the default filename index.txt will be used. If -I is not used, the program will load an index into memory from the index file. 

To control the number of results to return, use -n followed by a number.

To remove punctuation from the query, use -k.


