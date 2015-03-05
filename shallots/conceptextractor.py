from gensim import models

#select text  belonging to the cluster
for cluster in clusters: #should be id matching table

    model = models.Word2Vec()
    for word_1 in model.vocab:
        #decide on filtering on only most relevant words. Experiment with
        for word_2, score in model.most_similar(word_1, topn=3):
            cur.execute("INSERT INTO clusterwordvecs VALUES(%d, %s, %s, %.3f)", \
                        (cluster, word_1, word_2, score))


            cur.execute("SELECT exists(SELECT * FROM information_schema.tables WHERE table_name=%s)", \
                ('sites',))