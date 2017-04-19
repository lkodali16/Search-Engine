#!/usr/bin/python2

from Evaluation import Evaluation

score = {}
p_k = [5,20]
f = open('task1_bm25.txt','r')
output = f.readlines()
f.close()
for line in output:
  words = line.split()
  if score.has_key(words[0]):
    score[words[0]].append((words[2],words[4]))
  else:
    score[words[0]] = []
    score[words[0]].append((words[2],words[4]))

e = Evaluation(score,p_k)
e.evaluation()
