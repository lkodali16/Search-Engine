import os
import glob
import math
import string
import operator
import Indexer
import re

class Retriever:
    def __init__(self, corpus_directory, I):
        self.corpus_directory = corpus_directory
        # parser = indexer.Parser()
        # self.I = Indexer.InvertedIndexer(self.corpus_directory)
        self.I = I
        self.query_dic = {}  # stores the parsed query and its frequency
        self.score_dic = {}  # scores of each document
        self.current_query = ''     # used to open the file with query name and save results

        self.avdl = 0;  # average doc length
        self.first_query = True

    def build_indexes(self):
        # parser = indexer.Parser()
        # parser.build_corpus(self.raw_corpus_directory)
        # I = indexer.InvertedIndexer(self.raw_corpus_directory)
        self.I.ngram_indexer(1)

    def get_scores_for_docs(self, model = 'bm25'):
        if model == 'bm25':     # use bm25 retrieval model
            if self.first_query:
                self.first_query = False
                # initialize score_dic to zero
                for each_doc in self.I.doc_lengths:
                    self.avdl += self.I.doc_lengths[each_doc]
                self.avdl = float(self.avdl) / len(self.I.doc_lengths)
            for each_file in self.I.docIDs:
                BM25_score = 0
                for each_query_term in self.query_dic:
                    BM25_score += self.calculate_BM25_score(each_query_term, each_file)
                self.score_dic[each_file] = BM25_score

        if model == 'tfidf':    # use tf-idf retrieval model
            for each_file in self.I.docIDs:
                tfidf_score = 0
                for each_query_term in self.query_dic:
                    fk = 0  # number of occurrences of term k in document
                    doc_len = self.I.doc_lengths[each_file]
                    if each_query_term in self.I.inverted_indexes:
                        if each_file in self.I.inverted_indexes[each_query_term]:
                            fk = self.I.inverted_indexes[each_query_term][each_file]
                    else:
                        continue
                    tf = float(fk) / doc_len
                    idf = math.log(float(len(self.I.docIDs)) / len(self.I.inverted_indexes[each_query_term]))
                    tfidf_score += (tf * idf)
                self.score_dic[each_file] = tfidf_score

        # sort the documents based on scores
        sorted_docs = sorted(self.score_dic.items(), key=operator.itemgetter(1), reverse=True)
        docs = [x[0] for x in sorted_docs]
        scores = [x[1] for x in sorted_docs]
        return docs, scores

    def calculate_BM25_score(self, query_term, docID):     # query_term - single word in the whole query
        N = len(self.I.docIDs)
        n = 0
        f = 0
        if query_term in self.I.inverted_indexes:
            n = len(self.I.inverted_indexes[query_term])
            if docID in self.I.inverted_indexes[query_term]:
                f = self.I.inverted_indexes[query_term][docID]
        qf = self.query_dic[query_term]
        k1 = 1.2
        b = 0.75
        k2 = 100
        dl = self.I.doc_lengths[docID]
        K = k1*((1-b) + (b*(dl/self.avdl)))
        BM25_score_per_query = math.log(((float(N) - n + 0.5) / (n + 0.5))) * \
                               (float((k1 + 1)*f) /(K+f)) * \
                               ((float((k2 + 1) * qf)) / float(k2 + qf))

        return BM25_score_per_query

    def process_query(self, query):  # similar to process used while parsing corpus
        query = query.lower()
        self.current_query = query
        special_chars = re.sub("[,.-:]", "", string.punctuation)
        ignore_list = ['!', '@', '#', '$', '^', '&', '*', '(', ')', '_', '+', '=', '{', '[', '}', ']', '|',
                       '\\', '"', "'", ';', '/', '<', '>', '?', '%']
        query = query.translate(None, ''.join(ignore_list))
        query = query.replace(':', " ")
        query = query.replace('-', ' ')     # to split the words containg '-' symbol
                                            # eg: multi-targeted to 'multi', 'targeted'
        tokens = query.split()
        self.query_dic = {}
        for each_token in tokens:
            query = each_token.strip('.,-')
            self.query_dic[each_token] = 0
        for each_token in tokens:
            self.query_dic[each_token] += 1     # term frequency

def hw4():
    directory = raw_input('Enter corpus directory: ')
    if not os.path.exists(directory):
        print "Please enter valid directory address"
        directory = raw_input()
    r = Retriever(directory)
    r.build_indexes()
    e = False   # e - exit
    while not e:
        query = raw_input("Enter the Query: ")
        while not query:
            query = raw_input("Enter the Query: ")
        if query == 'e':
            e = True
            break
        r.process_query(query)
        r.get_scores_for_docs()




