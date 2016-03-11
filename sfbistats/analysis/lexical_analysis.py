# -*- coding: utf-8 -*-
""" Lexical analysis

This module provide some basic lexical analysis capabilities for the corpus of job descriptions.
It computes words rankings, frequencies and positions, which are used to output wordclouds and tendency curves.

It uses 3 main structures:
 - lex_dic: { word: count} a dictionary containing the total number of occurrence of each word in all the corpus.
 - pos_dic: {word: [pos1, pos2]} a dictionary pointing to a list of position where the word was found relative to
a text's length.
 - ordered_freq_list: [[word, frequency], ...] a list of tuples, as required for the input of the Wordcloud module.

"""

from random import Random
import re
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def get_stopwords():
    """
    return a dict of unicode strings containing all english AND french words to filter out, all lowercase

    Returns
    -------
    stopword_dict

    """
    stopword_dict = dict()
    f_en = open('stopwords_en.txt', 'r')
    for line in f_en.readlines():
        stopword_dict[line.strip().lower()] = True
    f_en.close()
    f_fr = open('stopwords_fr.txt', 'r')
    for line in f_fr.readlines():
        a = line.strip().lower().decode('utf8')
        stopword_dict[a] = True
    f_fr.close()
    return stopword_dict


def my_color_func(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    """
    custom colors for wordcloud, derived from wordcloud source

    Parameters
    ----------
    word
    font_size
    position
    orientation
    font_path
    random_state

    Returns
    -------

    """

    if random_state is None:
        random_state = Random()
    return "hsl(%d, 70%%, 40%%)" % random_state.randint(0, 255)


def build_lex_dic(corpus, stopword_dict= {}, separator=u"[\s,.\(\)!?/:;\[\]\{\}\u2019']+"):
    """

    Parameters
    ----------
    corpus
    stopword_dict
    separator

    Returns
    -------

    """
    lex_dic = dict()
    for text in corpus:
        for tkn in re.split(separator, text):
            tkn = tkn.lower()
            # don't keep stopwords, and skip weird characters and whitespace
            if tkn in stopword_dict or not re.match('\w+', tkn):
                continue
            if tkn in lex_dic:
                lex_dic[tkn] += 1
            else:
                lex_dic[tkn] = 1
    return lex_dic


def build_pos_dic(corpus, stopword_dict= {}, separator=u"[\s,.\(\)!?/:;\[\]\{\}\u2019']+"):#, bins=100):
    """

    Parameters
    ----------
    corpus
    stopword_dict
    separator

    Returns
    -------

    """
    pos_dic = dict()
    for text in corpus:
        word_pos = 0
        text_pos_dic = dict()
        for tkn in re.split(separator, text):
            tkn = tkn.lower()
            # don't keep stopwords, and skip weird characters and whitespace
            if tkn in stopword_dict or not re.match('\w+', tkn):
                continue
            if tkn in text_pos_dic:
                text_pos_dic[tkn].append(word_pos)
            else:
                text_pos_dic[tkn] = [word_pos]
            word_pos += 1
        # convert word positions in percentage of the text
        text_length = word_pos
        #print "text length: "+str(text_length)
        #pprint(text_pos_dic)
        for tkn, pos_list in text_pos_dic.iteritems():
            for e in pos_list:
                if tkn in pos_dic:
                    pos_dic[tkn].append(np.floor(float(e) / text_length * 100) )
                else:
                    pos_dic[tkn] = [np.floor(float(e) / text_length * 100)]
    return pos_dic


def get_total_words(lex_dic):
    total = 0
    for k, v in lex_dic.iteritems():
        total += v
    return total


def build_freq_list(lex_dic, total):
    freq_list = list()
    for e in sorted(lex_dic, key=lex_dic.get, reverse=True):
       freq_list.append([e, float(lex_dic[e]) / total])
    return freq_list


def create_wordcloud(ordered_freq_list, output):
    plt.figure(figsize=(10,8))
    wordcloud = WordCloud(width=1000, height=800, max_words=100, background_color='white',
                          relative_scaling=0.7, random_state=15, prefer_horizontal=0.5) .generate_from_frequencies(ordered_freq_list[0:100])
    wordcloud.recolor(random_state=42, color_func=my_color_func)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig(output, bbox_inches='tight', facecolor='white')


def get_rank(word, ordered_freq_list):
    rank = 1
    for pair in ordered_freq_list:
        if pair[0] == word:
            return rank
        rank += 1
    raise Exception("Word "+word+" not found")


def plot_tendency(word, pos_dic, bin_size, output_dir, file_name):
    plt.figure()
    if not word in pos_dic:
        raise Exception('Word '+word+' notfound')

    df = pd.DataFrame(pos_dic[word], columns=['pos'])#.groupby(['pos'])['pos'].count()
    df['bins'] = pd.cut(df['pos'], bins=range(0,100+bin_size,bin_size), labels=range(0,100,bin_size))
    df = df.groupby(['bins'])['bins'].count()
    ax = df.plot(title="Position du mot '"+word+"' dans les descriptions des offres")
    ax.set_xlabel("Position (en % de la longueur de la description)")
    ax.set_ylabel("Nombre d'occurrences")
    plt.savefig(os.path.join(output_dir, file_name), bbox_inches='tight')


def plot_tendencies(word_list, pos_dic, bin_size, output_dir, file_name):
    plt.figure()
    dataframe_list = list()
    for word in word_list:
        if not word in pos_dic:
            raise Exception('Word '+word+' not found')
        df = pd.DataFrame(pos_dic[word], columns=['pos'])
        df['bins'] = pd.cut(df['pos'], bins=range(0,100+bin_size,bin_size), labels=range(0,100,bin_size))
        df = df.groupby(['bins'])['bins'].count()
        dataframe_list.append(df)

    df_final = pd.DataFrame(pd.concat(dataframe_list, axis=1)).fillna(0)
    df_final.columns = word_list
    ax = df_final.plot()
    ax.set_xlabel("Position (en % de la longueur de la description)")
    ax.set_ylabel("Nombre d'occurrences")
    plt.title('Position des mots dans les descriptions des offres', y=1.08)
    plt.savefig(os.path.join(output_dir, file_name), bbox_inches='tight')

def run(job_list, output_dir):

    stopword_dict = get_stopwords()
    # add some stuff that isn't in the stopwords lists
    stopword_dict['-'] = True
    stopword_dict['dot'] = True
    stopword_dict['fr'] = True
    stopword_dict['www'] = True
    stopword_dict['http'] = True
    stopword_dict['al'] = True

    corpus = list()
    for job in job_list:
        corpus.append(job['title'])

    lex_dic = build_lex_dic(corpus, stopword_dict=stopword_dict)
    pos_dic = build_pos_dic(corpus, stopword_dict=stopword_dict)#, bins=100)
    total_words= get_total_words(lex_dic)
    ordered_freq_list = build_freq_list(lex_dic, total_words)

    create_wordcloud(ordered_freq_list, os.path.join(output_dir, 'figure_2_3.png'))

    print "TOTAL unique words: " + str(len(lex_dic))
    print "TOTAL words: " + str(total_words)
    """
    print "bioinformatique " + str(get_rank('bioinformatique', ordered_freq_list))
    print "Perl " + str(get_rank('perl', ordered_freq_list))
    print "Java " + str(get_rank('java', ordered_freq_list))
    print "Fortran " + str(get_rank('fortran', ordered_freq_list))
    print "web " + str(get_rank('web', ordered_freq_list))
    print "python " + str(get_rank('python', ordered_freq_list))
    print "html " + str(get_rank('html', ordered_freq_list))
    print "sql " + str(get_rank('sql', ordered_freq_list))
    print "hiseq " + str(get_rank('hiseq', ordered_freq_list))
    print "chip-seq " + str(get_rank('chip-seq', ordered_freq_list))
    print "css " + str(get_rank('css', ordered_freq_list))
    print "paris " + str(get_rank('paris', ordered_freq_list))
    print "c# " + str(get_rank('c#', ordered_freq_list))
    print "c++ " + str(get_rank('c++', ordered_freq_list))
    print "matlab  " + str(get_rank('matlab', ordered_freq_list))
    """

    #plot_tendencies(['perl', 'java', 'python', 'c++'], pos_dic, 5, output_dir, 'figure_2_2.png')

