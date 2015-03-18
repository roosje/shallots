from operator import itemgetter
import numpy as np
from sklearn import decomposition
from sklearn.feature_extraction.text import TfidfVectorizer


class topic_model(object):
    def __init__(self):
        self.nmf = None

    def nmf_model(self, texts, n_topics, vectorizer):
        '''
        INPUT: LIST OF LISTS OF TOKENIZED TEXTS, INT, VECTORIZER OBJECT
        OUTPUT: DICT
        Builds topic model on pre-tokenized/tfidf vectorized texts with NMF
        looking for n_topics different topics
        '''
        n_words = 10
        self.nmf = decomposition.NMF(n_components=n_topics, init='nndsvd',
                                     beta=10)
        self.nmf.fit(texts)
        vocab = np.array(vectorizer.get_feature_names())
        topic_words = []
        for topic in self.nmf.components_:
            word_idx = np.argsort(topic)[::-1][0:n_words]
            topic_words.append([vocab[i] for i in word_idx])
        topics_descr = {}
        for t in range(len(topic_words)):
            terms = ' '.join(topic_words[t][:n_words])
            topics_descr[t] = terms
        return topics_descr

    def nmf_predict(self, tokenized):
        '''
        INPUT: LIST of STRINGS
        OUTPUT: INT
        Returns the most likely topic based on the given set of words.
        '''
        assigned = self.nmf.transform(tokenized)
        return np.argmax(assigned)
