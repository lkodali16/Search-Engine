from bs4 import BeautifulSoup
import os
import Indexer
import Retriever

p = Indexer.Parser()
raw_corpus_directory = raw_input("Enter the raw corpus directory (html files): ")
corpus_directory = p.build_corpus(raw_corpus_directory, stopped = True)

I = Indexer.InvertedIndexer(corpus_directory)
I.ngram_indexer(1) # builds a unigram indexes for each word
r = Retriever.Retriever(corpus_directory, I)    # create a Retriever class, which contains different retrieval model

os.chdir(raw_corpus_directory)
os.chdir(os.pardir)
f = open('cacm.query.txt', 'r')
soup = BeautifulSoup(f.read(), 'html.parser')
f.close()

f_stop_words = open('common_words.txt', 'r')
stop_words_list = f_stop_words.readlines()
stop_words = [i.strip() for i in stop_words_list]
f_stop_words.close()

model = 'bm25'
f = open('task3a_'+ model + '.txt', 'w')     # open file for writing results
for i in range(64):
    query_no = (soup.find('docno')).text.encode('utf-8')    # extract query number and query
    (soup.find('docno')).decompose()
    query = (soup.find('doc')).text.encode('utf-8')
    (soup.find('doc')).decompose()

    r.process_query(query, stopped = True, stopwords = stop_words)          # parse the query
    # r.clean_content(query)
    docs_and_scores = r.get_scores_for_docs(model)   # retrieve relevant documents

    # save results into appropriate file
    docs = docs_and_scores[0]
    scores = docs_and_scores[1]
    for i in range(100):
        f.write(str(query_no) \
                    + " Q0 " \
                    + str(docs[i]) + ' ' \
                    + str((i+1)) + " " \
                    + str(scores[i]) + " " \
                    + "system_name\n")
f.close()