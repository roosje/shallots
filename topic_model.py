from gensim import corpora, models, similarities
#from itertools import chain
#import nltk
from operator import itemgetter

class topic_model(object):
    def __init__(self):
        self.tfidf = None
        self.dictionary = None
        self.lda = None

    def model(self, texts, n_topics):
        '''
        INPUT: LIST OF LISTS, already cleaned, lemmatizes, tokenizes and lowercased
               INT, number of topics the model should return
        OUTPUT: DICT (INT => LIST OF STRINGS), LdaModel

        Returns a dictionary with the topics and their top 10 words 
        '''
        
        #TFIDF
        self.dictionary = corpora.Dictionary(texts)
        corpus = [self.dictionary.doc2bow(text) for text in texts]
        self.tfidf = models.TfidfModel(corpus) 
        corpus_tfidf = self.tfidf[corpus]

        #lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=n_topics)
        #lsi.print_topics(10)

        self.lda = models.LdaModel(corpus_tfidf, id2word=self.dictionary, num_topics=n_topics)

        topics_descr = {}
        #show_topics(n_topics, 10) might be easier
        for i in range(0, n_topics):
            temp = self.lda.show_topic(i, 10)
            terms = []
            for term in temp:
                terms.append(term[1])
            topics_descr[i] = terms
        return topics_descr

    def predict(self, tokenized):
        '''
        INPUT: LIST of STRINGS
        OUTPUT: INT 

        Returns the most likely topic based on the given set of words.
        '''
        bow_vector = self.dictionary.doc2bow(tokenized)
        lst = self.lda[self.tfidf[bow_vector]]
        return max(lst, key=itemgetter(1))[0]

    