from gensim import models
from clean_tokenize import *
import re


def extract_and_store(con, cur, topics):
    '''
    INPUT: Postgres Connection, Cursor, LIST (if cluster id's)
    OUTPUT: -
    Finds sentences from all texts belonging to topics, calculates similarity
    between words and store most similar words per topic in postgres.
    '''
    print "finding similar words per cluster"
    for topic in topics:
        cur.execute("SELECT text FROM features \
                     WHERE cluster_id=%d;" % (topic))
        sentences = []
        for row in cur.fetchall():
            text = clean_tokenized_text(row[0])
            sentences.append(text)
        model = models.Word2Vec(sentences, size=1000, window=5, min_count=2,
                                workers=4)
        cur.execute("SELECT description FROM clusters \
                     WHERE cluster_id=%d;" % (topic))
        words = cur.fetchall()[0][0].split()
        for word_1 in words:
            if word_1 in model.vocab:
                for word_2, score in model.most_similar(word_1, topn=5):
                    print topic, word_1, word_2, score
                    cur.execute("INSERT INTO clusterwordvecs VALUES(%d, '%s', \
                                '%s', %.3f);" % (topic, word_1, word_2, score))
        con.commit()
