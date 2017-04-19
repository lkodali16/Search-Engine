from bs4 import BeautifulSoup
import os
import Indexer
import Retriever

model = raw_input("Enter the model: ")
raw_corpus_directory = raw_input("Enter the raw corpus directory (html files): ")
project_directory = os.getcwd()

# Parser (to process the raw corpus (no stopping))
p = Indexer.Parser()
corpus_directory = p.build_corpus(raw_corpus_directory)

# Indexer - Builds the inverted indexes for the processed corpus
I = Indexer.InvertedIndexer(corpus_directory)
I.ngram_indexer(1) # builds a unigram indexes for each word

# Retriever - based on the model specified, this object can  be
#             used to get the results.
r = Retriever.Retriever(corpus_directory, I)

# Get the queries from the given file
query_dic = {}      # stores the queries; key - query ID, token - query
os.chdir(project_directory)
f = open('cacm.query.txt', 'r')
soup = BeautifulSoup(f.read(), 'html.parser')
f.close()
for i in range(64):
    query_no = (soup.find('docno')).text.encode('utf-8')  # extract query number and query
    (soup.find('docno')).decompose()
    query = (soup.find('doc')).text.encode('utf-8')
    (soup.find('doc')).decompose()
    query_dic[int(query_no)] = query

# task 1
os.chdir(project_directory)
task1_directory = os.path.join(project_directory, "task1")
if not os.path.exists(task1_directory):
    os.mkdir(task1_directory, 0755)
os.chdir(task1_directory)

f = open('task1_'+model+'.txt', 'w')
for query_no in range(len(query_dic)):
    r.process_query(query_dic[query_no + 1])                           # parse the query
    docs_and_scores = r.get_scores_for_docs(model)   # retrieve relevant documents

    # save results into appropriate file
    docs = docs_and_scores[0]
    scores = docs_and_scores[1]
    for i in range(100):
        f.write(str(query_no + 1) \
                    + " Q0 " \
                    + str(docs[i]) + ' ' \
                    + str((i+1)) + " " \
                    + str(scores[i]) + " " \
                    + model + "\n")
f.close()

