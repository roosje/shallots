#!/usr/bin/env python
# -*- coding: utf-8 -*-

import add_languages
import setup_postgres
import extractcountries
import topic_model
import conceptextractor
from clean_tokenize import *

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

from psycopg2 import connect
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from sqlalchemy import Table, MetaData, create_engine

import pandas.io.sql as psql
import pandas as pd
import itertools
import json
import numpy as np

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

import sys
import os
import re


class shallots(object):

    def __init__(self):
        password = os.environ['roosje_pass']
        server = os.environ['aws_server']
        self.client = MongoClient(server, 27017)
        self.mongo_db = self.client.shallots.onions
        self.sql_dbname = 'shallots'
        self.con = connect(database=self.sql_dbname, user='postgres',
                           password=password, host=server)
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.con.cursor()
        self.n_topics = 15
        self.domains = set()
        self.engine = create_engine("postgresql://postgres:%s@%s/%s"
                                    % (password, server, self.sql_dbname))
        self.alchcon = self.engine.connect().connection

    def add_languages_mongo(self, stepsize, start):
        '''
        INPUT: INT, INT (used for breaking up the proces in smaller steps)
        Adds "language" field to mongodb based on "word" field
        '''
        add_languages.run(self.mongo_db, stepsize, start)

    def make_sql_database(self):
        '''
        Creates a new postgres database (drops all tables)
        '''
        # GET CURRENT TABLES
        self.cur.execute("SELECT relname FROM pg_class WHERE relkind='r' AND \
                          relname !~ '^(pg_|sql_)';")
        tables = [i[0] for i in self.cur.fetchall()]
        # DROP ALL TABLES
        for table in tables:
            setup_postgres.drop_table(self.con, self.cur, table)
        # CREATE NEW TABLES
        setup_postgres.create_tables(self.con, self.cur)

    def fill_mongoref_sql_database(self):
        '''
        Fills a SQL table with only references to the mongo ids
        for the domains that have the english language
        '''
        print "filling mongo ref table in sql"
        for res in self.mongo_db.find({"language": "en"},
                                      {"_id": 1, "domain": 1}):
            domainparts = res['domain'].split(".")
            domain = domainparts[-2] + "." + domainparts[-1]
            self.domains.add(domain)
            self.cur.execute('''INSERT INTO sites (mongo_id, domain) VALUES \
                            ('%s', '%s');''' % (str(res['_id']), domain))
        self.con.commit()

    def fill_sitesite_relations(self):
        '''
        Fills the relations SQL table with (onion) domain to domain references
        found in the html field in mongo
        '''
        print "filling dom-dom relations in sql"
        self.cur.execute('SELECT DISTINCT(domain) FROM sites;')
        self.domains = set([i[0] for i in self.cur.fetchall()])
        pattern = re.compile('([2-7a-z]+\.onion)')
        for d in self.domains:
            ref_domains = set()
            # GET HTML FROM MONGO FOR THAT DOMAIN
            htmls = self.mongo_db.find({"domain": d, "language": "en"},
                                       {'html': 1})
            # FIND DOMAINS IN HTML
            for page in htmls:
                results = pattern.findall(page['html'])
                for res in results:
                    ref_domains.add(res)
            # DISCARD D ITSELF
            ref_domains.discard(d)
            # DDISCARD EVERY DOMAIN THAT IS NOT IN THE DATABASE
            ref_domains.intersection_update(self.domains)
            for ref_dom in ref_domains:
                self.cur.execute('''INSERT INTO relations VALUES \
                                ('%s', '%s');''' % (d, ref_dom))
            self.con.commit()

    def group_text_store(self):
        '''
        Concats all the texts belonging to one domain into 1 text field
        '''
        print "concat text per domain and store"
        self.cur.execute("SELECT DISTINCT(domain) FROM sites;")
        self.domains = set([i[0] for i in self.cur.fetchall()])
        for d in self.domains:
            # SEARCH TEXT AND CONCAT
            text = " ".join(res['words'] for res in
                            self.mongo_db.find({"domain": d, "language": "en"},
                                               {'words': 1}))
            text = text.replace("'", " ")
            self.cur.execute('''INSERT INTO features (domain, text) \
                            VALUES('%s', '%s');''' % (d, text))
        self.con.commit()

    def fill_countries(self):
        '''
        Find the countries in the text and store in SQL
        '''
        extractcountries.run(self.con, self.engine)

    def find_topics_descr_and_store(self, n_topics, n_domains):
        '''
        INPUT: INT, INT (nr clusters and nr domains to build model on)
        Builds unsupervised topic model on n_domains of data to use to assign
        clusters to all seperate domains
        '''
        topicm = topic_model.topic_model()
        self.cur.execute("SELECT text FROM features \
                          ORDER BY RANDOM() \
                          LIMIT %d;" % (n_domains))
        texts = []
        for row in self.cur.fetchall():
            texts.append(row[0])

        # BUILDMODEL ON N_DOMAINS ROW
        tfidfvect = TfidfVectorizer(max_df=0.95, min_df=2,
                                    tokenizer=clean_tokenized_text)
        tfidf_vectorized = tfidfvect.fit_transform(texts)

        tpcs = topicm.nmf_model(tfidf_vectorized, n_topics, tfidfvect)
        for k, v in tpcs.iteritems():
            descr = v
            print k, descr
            self.cur.execute("INSERT INTO clusters (cluster_id, description) \
                              VALUES(%d, '%s');" % (k, descr))
        self.con.commit()

        # RUN ON EVERYTHING FOR ASSIGNING CLUSTERS
        self.cur.execute("SELECT domain, text FROM features;")
        for row in self.cur.fetchall():
            domain = row[0]
            text = tfidfvect.transform([unicode(row[1], errors='ignore')])
            pred = topicm.nmf_predict(text)
            self.cur.execute("UPDATE features SET cluster_id=%d WHERE \
                            domain='%s';" % (pred, domain))
        self.con.commit()

    def similar_extract(self):
        '''
        For the 10 most relevant words per topic,
        find similar words for later use
        '''
        topics = range(0, self.n_topics)
        conceptextractor.extract_and_store(self.con, self.cur, topics)

    def prepare_for_web(self):
        '''
        Prepare most of the needed files that the dashboard will need later
        '''
        # CODE FOR WORDCLOUD
        data = psql.read_sql("SELECT cluster_id AS cluster, text \
                        FROM features;", self.engine)
        data['text'] = data['text'].apply(lambda x: (clean_tokenized_text(x)))
        data = data.groupby('cluster')['text'].apply(lambda x:
                        list(itertools.chain.from_iterable(x))).reset_index()
        for i, row in data.iterrows():
            c = Counter(row['text'])
            filename = 'web/static/data/worddata'+str(i)+'.json'
            json.dump(c.most_common(50), open(filename, 'wb'))

        # CODE FOR GRAPH TOPIC BASED
        dataNodes2 = psql.read_sql("SELECT clusters.cluster_id AS tmp, size, \
                        cluster_name AS name FROM clusters JOIN \
                        (SELECT cluster_id, count(*) as size FROM features \
                        GROUP BY cluster_id) AS cl \
                        ON clusters.cluster_id = cl.cluster_id;", self.engine)
        dataNodes2['index'] = dataNodes2.index
        dataNodes2.rename(columns={'tmp': 'group'}, inplace=True)
        dataNodes2 = dataNodes2.set_index('group')
        dataLinks2 = psql.read_sql("SELECT cluster_id AS cluster_to, cluster_from, \
                        COUNT(*) AS value FROM features JOIN \
                        (SELECT cluster_id AS cluster_from, domain_to \
                        FROM features JOIN relations \
                        ON relations.domain_from = features.domain) \
                        AS prt1 ON prt1.domain_to = features.domain \
                        WHERE cluster_id <> cluster_from \
                        GROUP BY cluster_to, cluster_from;", self.engine)
        dataLinks2 = dataLinks2.join(dataNodes2['index'], on='cluster_from')
        dataLinks2.rename(columns={'index': 'source'}, inplace=True)
        dataLinks2 = dataLinks2.join(dataNodes2['index'], on='cluster_to')
        dataLinks2.rename(columns={'index': 'target'}, inplace=True)
        dataNodes2 = dataNodes2.reset_index()
        dataNodes2.to_json('web/static/data/nodes2.json', orient="records")
        dataLinks2.to_json('web/static/data/links2.json', orient="records")

        # CODE FOR PIE DONUT CHART
        dataPie = psql.read_sql("SELECT cluster_id as category, \
                        ROUND(COUNT(*)*1.0/SUM(COUNT(*)) OVER(),2) AS measure \
                        FROM features \
                        GROUP BY cluster_id;", self.engine)
        dataPie.to_json('web/static/data/piedata.json', orient="records")


if __name__ == '__main__':
    print "starting pipeline"
    shal = shallots()

    # ADD "LANGUAGE" FIELD TO MONGODB
    shal.add_languages_mongo(stepsize=1000, start=0)

    # DROP, MAKE DATABASES & TABLES POSTGRES
    shal.make_sql_database()

    # FILL TABLES WITH REFERRALS TO MONGO ID
    # (FILTER IN ENGLISH LANGUAGE)
    shal.fill_mongoref_sql_database()

    # EXTRACT DOMAINS FROM HTML AND STORE IN TABLE
    shal.fill_sitesite_relations()

    # CLEAN AND CONCAT TEXT AND STORE IN TABLE
    shal.group_text_store()

    # REMOVE THIS FILE TO START OVER WITH EXTRACTING COUNTRIES
    os.remove('data/countries.pkl')

    # EXTRACT COUNTRIES AND STORE IN TABLE
    shal.fill_countries()

    # STORE CLUSTERS AND THEIR DESCRIPTION
    # PLUS STORE CLUSTER ASSIGNMENTS
    shal.cur.execute("DELETE FROM clusters WHERE true;")
    shal.con.commit()
    shal.find_topics_descr_and_store(n_topics=shal.n_topics, n_domains=500)

    # WITHIN CLUSTES, DO SIMILAR CONCEPT EXTRACTION AND STORE
    shal.cur.execute("DELETE FROM clusterwordvecs WHERE true;")
    shal.con.commit()
    shal.similar_extract()

    # PREPARE FILES FOR THE ONLINE DASHBOARD
    shal.prepare_for_web()

    # CLOSE ALL THE CONNECTIONS
    shal.cur.close()
    shal.con.close()
    shal.client.close()
    shal.alchcon.close()

    # INSERT HANDWORK ANNOTATIONS FOR LEGAL/ILLEGAL CLUSTERS
    # INSERT HANDWORK NAMING OF CLUSTERS
    # AFTER THAT TIME TO VISUALIZE
