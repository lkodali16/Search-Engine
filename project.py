#!/usr/bin/python2
import os
import glob
from Evaluation import Evaluation


project_directory = os.getcwd()
output_directory = os.path.join(project_directory, "output")

print "Select a task number\n\t1. Task - 1 " \
      "\n\t2. Task - 2 " \
      "\n\t3. Task - 3a" \
      "\n\t4. Task - 3b" \
      "\n\t5. Phase - 2" \
      "\n\t6. t-test" \
      "\n\t7. Snippet Generation"

task = int(raw_input())

if task == 5:
    evaluation_directory = os.path.join(project_directory, "evaluation_output")
    if not os.path.exists(evaluation_directory):
        os.mkdir(evaluation_directory, 0755)

    file_names = ["task1_bm25.txt", "task1_tfidf.txt", "task1_lucene.txt",
                  "task2_bm25.txt", "task2_tfidf.txt",
                  "task3a_bm25.txt", "task3a_tfidf.txt"]
    for each_file in file_names:
        score = {}
        p_k = [5,20]
        f = open(os.path.join(output_directory, each_file), 'r')
        output = f.readlines()
        f.close()
        for line in output:
            words = line.split()
            if score.has_key(words[0]):
                score[words[0]].append((words[2],words[4]))
            else:
                score[words[0]] = []
                score[words[0]].append((words[2],words[4]))
        filename = os.path.join(evaluation_directory, each_file)
        e = Evaluation(score, p_k, filename)
        e.evaluation()
