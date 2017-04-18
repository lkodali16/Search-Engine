from bs4 import BeautifulSoup
import re
import string
import requests
import os
import glob
import operator
import math
import time
import sys

class Parser:
    def __init__(self):
        self.corpus_directory = ''      # this contains cleaned corpus directory
                                        # this variable is populated in generate_corpus() function
        self.stop_words = []

    def parse_file(self, file_name):     # file_name -> file containing raw html data
        parsed_text = ''
        f = open(file_name, 'r')
        html_page = f.read()
        soup = BeautifulSoup(html_page, 'html.parser')
        main_text = soup.get_text().encode('utf-8')

        special_chars = re.sub("[,.-:]", "", string.punctuation) # contains string of special chars
        special_chars = special_chars.replace('-', "")
        ignore_list = ['!', '@', '#', '$', '^', '&', '*', '(', ')', '_', '+', '=', '{', '[', '}', ']', '|',
                       '\\', '"', "'", ';', '/', '<', '>', '?', '%']
        main_text = main_text.translate(None, ''.join(ignore_list))    # delete chars present in special_chars
        main_text = main_text.replace(':', ' ')     # to split hours and minutes
        main_text = main_text.replace('-', ' ')     # to split the words containg '-' symbol
                                                    # eg: multi-targeted to 'multi', 'targeted'
        main_text = main_text.split()

        index = 0
        length = len(main_text)
        for i in range(length):     # to remove the content after AM and PM
            if 'AM' in main_text[length - i - 1]:
                # index = len(main_text) - i - 1
                break
            elif 'PM' in main_text[length - i - 1]:
                # index = len(main_text) - i - 1
                break
            main_text.pop(length - i - 1)
        # for i in range(index - len(main_text)): # pop number after AM and PM in main_text list
            # main_text.pop(index + i + 1)

        for each_word in main_text:
            each_word = each_word.lower()
            each_word = each_word.strip('.-,')   # remove '.', '-' from beginning and ending of the word
            # each_word = re.sub("x[a-z][0-9]", "", each_word)    #removing special chars
            '''if re.search("[0-9]", each_word):
                if(re.search("[a-z]", each_word)):
                    each_word = re.sub("[.,]", "", each_word)
                parsed_text += each_word + ' '
            else:
                each_word = re.sub("[.,]", "", each_word)   # since it is not a number, remove '.', ',' '''
            if each_word == '':
                continue
            parsed_text += each_word + ' '

        f.close()
        file_name = os.path.join(self.corpus_directory, file_name)
        print file_name
        f = open(file_name, 'w')
        f.write(parsed_text)
        f.flush()
        f.close()

    def build_corpus(self, raw_corpus_directory, stopped = False):
        # create a directory to store parsed documents
        '''if raw_corpus_directory == os.path.abspath(os.path.join(os.pardir, 'corpus')):
            self.corpus_directory = os.path.abspath(os.path.join(os.pardir, 'parsed_corpus'))
        else:
            self.corpus_directory = os.path.abspath(os.path.join(os.pardir, 'corpus'))'''
        self.corpus_directory = os.path.abspath(os.path.join(os.getcwd(), 'parsed_corpus'))
        if stopped:
            f = open('')
        if not os.path.exists(self.corpus_directory):
            os.mkdir(self.corpus_directory, 0755)
            print "created directory", self.corpus_directory
        print "parsed files are saved into ", self.corpus_directory
        os.chdir(raw_corpus_directory)
        files_list = glob.glob('*.html')
        for each_file in files_list:
            self.parse_file(each_file)
        return self.corpus_directory


class InvertedIndexer:
    def __init__(self, corpus_directory):
        self.corpus_directory = corpus_directory
        self.docIDs = {}        # contains ID assigned for each document(text file)
        self.inverted_indexes = {}  # contains inverted indexes for each word
        self.doc_lengths = {}        #to store number of tokens in each document
                                    # key - doc ID; value - doc length
        self.tf_table = {}      # stores tf table
        self.df_table = {}


    def ngram_indexer(self, n):
        # generate doc Id's for each document using links(used to generate corpus)
        print "Generating Inverted Indexes for ", n," gram, using files in corpus directory ..."
        os.chdir(self.corpus_directory)
        files_list = glob.glob('*.html')
        id_of_doc = 1
        for each_file in files_list:
            self.docIDs[each_file[:len(each_file)-5]] = id_of_doc
            id_of_doc += 1

        # populate inverted indexes dictionary with token and its
        # respective inverted index(another dictionary with dicID and tf)
        for each_file in files_list:
            f = open(each_file, 'r')
            data = f.read()
            f.close()
            each_file = each_file[:len(each_file)-5]    # to remove '.html' from end of the filename
            token_list = data.split()

            # --------------------------------------------------------
            # remove stop words from token_list if stopping is enabled
            # --------------------------------------------------------

            if n == 1:
                self.doc_lengths[each_file] = len(token_list)   # to save number of tokens in each document
            else:
                # generate WORD's (word n-gram)
                ngram = zip(*[token_list[i:] for i in range(n)])
                token_list = []
                for each_token in ngram:
                    token_list.append(' '.join(list(each_token)))
                self.doc_lengths[each_file] = len(token_list)

            for each_token in token_list:
                if each_token not in self.inverted_indexes:
                    # create a dictionary and add it to inverted indexes
                    inv_index = {}
                    inv_index[each_file] = 1
                    self.inverted_indexes[each_token] = inv_index

                else:
                    # update tf
                    if each_file not in self.inverted_indexes[each_token]:
                        self.inverted_indexes[each_token][each_file] = 1
                    else:
                        self.inverted_indexes[each_token][each_file] += 1
        # print self.inverted_indexes
        # f = open('Inverted_indexes.txt', 'w')
        # sys.stdout = open('Inverted_indexes.txt', 'w')
        # print self.inverted_indexes
        # sys.stdout.close()

    def corpus_statistics(self, n, save = False):
        print "Generating tf table"
        for each_word in self.inverted_indexes:
            self.tf_table[each_word] = 0
            for each_doc in self.inverted_indexes[each_word]:
                self.tf_table[each_word] += self.inverted_indexes[each_word][each_doc]

        if os.getcwd() == self.corpus_directory:
            os.chdir(os.pardir)
        # save sorted table into a file
        sorted_words = sorted(self.tf_table.items(), key = operator.itemgetter(1), reverse=True)
        words = [x[0] for x in sorted_words]
        tf = [x[1] for x in sorted_words]

        if save:
            f = open('tf_table_' + str(n) + '_gram.txt', 'w')
            for i in range(len(self.tf_table)):
                f.write(str(words[i]) + '\t' + str(tf[i]) + '\n')
            f.flush()
            f.close()

        print "Generating df table"
        word_list = []
        for k,v in self.inverted_indexes.viewitems():
            word_list.append(k)
        sorted_words = sorted(word_list)
        for each_word in sorted_words:
            self.df_table[each_word] = []
            for k,v in self.inverted_indexes[each_word].viewitems():
                self.df_table[each_word].append(k)

        if save:
            f = open('df_table_' + str(n) + '_gram.txt', 'w')
            for each_word in sorted_words:
                f.write(str(each_word) + ' ' + str(self.df_table[each_word]) + ' ' + str(len(self.df_table[each_word])) + '\n')

    def stoplist(self):
        stop_words = {}
        print "Generating idf values for each word"
        for key,value in self.tf_table.viewitems():
            #tf = self.tf_table[each_word]
            idf = math.log(float(len(self.docIDs))/len(self.df_table[key]), 2)
            stop_words[key] = idf
        sorted_stop_words = sorted(stop_words.items(), key=operator.itemgetter(1), reverse=False)
        if os.getcwd() == self.corpus_directory:
            os.chdir(os.pardir)
        f = open('stop_list.txt', 'w')
        for each_word in sorted_stop_words:
            f.write(str(each_word[0]) + ' ' + str(stop_words[each_word[0]]) + '\n')

def build_corpus(file_name):
    corpus_directory = os.path.join(os.getcwd(), 'raw_corpus')    #get corpus directory and check whether it exists
    if not os.path.exists(corpus_directory):
        print "created directory named \"raw_courpus\" "
        print "downloading html file ..."
        os.makedirs(corpus_directory, 0755)     #creating directory with normal access flags
    f = open(file_name, 'r')
    urls = f.read().splitlines()
    f.close()
    os.chdir(corpus_directory)
    for eachUrl in urls:
        try:
            html_page = requests.get(eachUrl)
        except:
            print "problem in accesing", eachUrl
            continue

        file_name = eachUrl[30:]
        file_name = file_name.translate(None, string.punctuation)   # removes punctuation from the filename
        file_name = file_name + '.txt'
        f = open(file_name, 'w')
        f.write(html_page.text.encode('utf-8'))
        f.flush()
        f.close()
    os.chdir(os.pardir)


def hw3():
    file_name = raw_input('Input filename containing links: ')
    #build_corpus(file_name)
    #p = Parser()
    #p.generate_corpus()

    # If p object is created uncomment below line to pass corpus_directory to InvertedIndexer
    #corpus_directory = p.corpus_directory

    # If parser object is not created, uncomment these lines
    # ------------------------------------------------------
    #
    corpus_directory = os.getcwd()
    corpus_directory = os.path.join(corpus_directory, 'corpus')
    #
    # ------------------------------------------------------

    I = InvertedIndexer(corpus_directory)
    I.ngram_indexer(3)
    # print I.inverted_indexes
    I.corpus_statistics(3)
    # I.stoplist()    # only of unigrams

# hw3()