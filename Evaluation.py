#!/usr/bin/python2

import pdb
from operator import itemgetter

class Evaluation:

    def __init__(self,query_results,p_k):
        self.query_results = query_results #Give the document results corresponding to the query_id.
        self.p_k = p_k

    def evaluation(self):
        query_relevant = {}
        query_results = self.query_results

        #Store the relevant documents corresponding to a query into a dictionary.
        relevant = open('cacm.rel','r')
        for line in relevant.readlines():
          words = line.split()
          if query_relevant.has_key(words[0]):
            query_relevant[words[0]].append(words[2])
          else:
            query_relevant[words[0]] = []
            query_relevant[words[0]].append(words[2])

        relevant.close()

        #Calculate the recall and precision scores for a run.
        precision_recall_query = {}
        scores = {}
        seq_docs = {}
        MAP = [] 
        MRR = []
        for query_id,docs in query_results.viewitems():
          try:
            total_relevant_docs_query = len(query_relevant[query_id])
            precision_recall_query[query_id] = {}
            scores[query_id] = {}
            seq_docs[query_id] = []
            precision_sum = 0
            relevance_rank = 0
            relevant_doc = 0
            relevancy = 0
            count = 0

            for doc in docs:
              if doc[0] in query_relevant[query_id]:
                relevant_doc += 1
                relevancy = 1
                precision_sum += float(relevant_doc)/(docs.index(doc)+1)

              if relevant_doc == 1 and count < 1:
                count += 1
                relevance_rank = 1 / float(docs.index(doc)+1)

              scores[query_id][doc[0]] = doc[1]
              precision = float(relevant_doc)/(docs.index(doc)+1)
              recall = float(relevant_doc)/ len(query_relevant[query_id])
              precision_recall_query[query_id][doc[0]] = (precision,recall)
              seq_docs[query_id].append(doc[0])
            
            avg_precision = float(precision_sum)/relevant_doc
            MAP.append(avg_precision)
            MRR.append(relevance_rank) 
          except KeyError:
            continue

        total_querys = [int(key) for key in precision_recall_query]
        total_querys.sort()
        total_querys = [str(key) for key in total_querys]
        map_result = sum(MAP)/len(MAP)
        mrr_result = sum(MRR)/len(MRR)
        file1 = open('output.txt','w')
        for query in total_querys:
          rank = 0
          for doc_id in seq_docs[query]:
            rank += 1
            if doc_id in query_relevant[query]:
              file1.write("{} {} {} {} {} {} {}".format(query,rank,doc_id,scores[query][doc_id],1,precision_recall_query[query][doc_id][0],precision_recall_query[query][doc_id][1]) + '\n')
            else:
              file1.write("{} {} {} {} {} {} {}".format(query,rank,doc_id,scores[query][doc_id],0,precision_recall_query[query][doc_id][0],precision_recall_query[query][doc_id][1]) + '\n')

        file1.close() 
