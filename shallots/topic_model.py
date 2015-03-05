from gensim import corpora, models, similarities
from itertools import chain
import nltk
from nltk.corpus import stopwords
from operator import itemgetter
import re

def model(documents, n_topics):
    #lemma
    #remove stopwords
    #tokenize
    #tfidf

    #data is already cleaned and lowercased
    #documents = [document for document in data]
    stoplist = stopwords.words('english')
    texts = [[word for word in document.split() if word not in stoplist]
              for document in documents] #list of lists

    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]

    tfidf = models.TfidfModel(corpus) 
    corpus_tfidf = tfidf[corpus]

    #lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=n_topics)
    #lsi.print_topics(10)

    lda = models.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=n_topics)

    topics_descr = {}
    for i in range(0, n_topics):
        temp = lda.show_topic(i, 10)
        terms = []
        for term in temp:
            terms.append(term[1])
        topics_descr[i] = terms

    return topics_descr