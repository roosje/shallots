from gensim import models

def extract_and_store(con, cur, topics):
	'''
	INPUT: Postgres Connection, Cursor, LIST (if cluster id's)
	OUTPUT: -

	Finds sentences from all texts belonging to topics, calculates similarity 
	between words and store most similar words per topic in postgres.
	'''
	for topic in topics: 
	    self.cur.execute("SELECT text FROM features2 WHERE cluste_id='%s';" %(topic))
	    sentences = [i[0] for i in self.cur.fetchall()]
	    model = models.Word2Vec(sentences, size=100, window=5, min_count=5, workers=4)
	    for word_1 in model.vocab:
	        #decide on filtering on only most relevant words. Experiment with
	        for word_2, score in model.most_similar(word_1, topn=3):
	            cur.execute("INSERT INTO clusterwordvecs VALUES(%d, %s, %s, %.3f)", \
	                        (topic, word_1, word_2, score))
	    con.commit()