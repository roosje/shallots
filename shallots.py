#!/usr/bin/env python
# -*- coding: utf-8 -*-

import add_languages
import setup_postgres
import extractcountries
import topic_model
import conceptextractor

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

from psycopg2 import connect
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from sqlalchemy import Table, MetaData, create_engine

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

import sys
import os
import re

class shallots(object):
    def __init__(self):
        password = os.environ['roosje_pass']
        server = os.environ['aws_server']
        
        self.client = MongoClient(server, 27017)
        self.mongo_db = self.client.scrapy.onions
        self.sql_dbname= 'shallots'
        self.con = connect(database=self.sql_dbname, user ='postgres', \
                           password=password, host=server)
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.con.cursor()
        self.topics = {}
        self.domains = set()
        self.engine = create_engine("postgresql://postgres:%s@%s/%s" \
                      %(password, server, self.sql_dbname))
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
        #select only english
        #get mongo_id
        #store in sql
        print "filling mongo ref table in sql"
        for res in self.mongo_db.find({"language": "en"},{"_id":1, "domain":1}):
            domainparts = res['domain'].split(".")
            domain = domainparts[-2] + "." + domainparts[-1]
            self.domains.add(domain)
            #insert into sites fields: mongo_id and domain, site_id is serial
            self.cur.execute('''INSERT INTO sites (mongo_id, domain) VALUES \
                            ('%s', '%s');''' %(str(res['_id']), domain))
        self.con.commit()
        


    def fill_sitesite_relations(self):
        print "filling dom-dom relations in sql"
        self.cur.execute('SELECT DISTINCT(domain) FROM sites;')
        self.domains = set([i[0] for i in self.cur.fetchall()])
        pattern = re.compile('([2-7a-z]+\.onion)')
        for d in self.domains:
            ref_domains = set()
            #get html from mongo for that domain
            htmls = self.mongo_db.find({"domain": d},{'html':1})
            #find domains in htmls
            for page in htmls:
                results = pattern.findall(page['html'])
                for res in results:
                    ref_domains.add(res)
            #discard d itself        
            ref_domains.discard(d)
            #discard every domain that is not in the database
            ref_domains.intersection_update(self.domains)
            for ref_dom in ref_domains:
                #store d, domains in relations
                self.cur.execute('''INSERT INTO relations VALUES \
                                ('%s', '%s');''' %(d, ref_dom))
            self.con.commit()    



    def group_text_store(self):
        print "concat text per domain and store"
        self.cur.execute("SELECT DISTINCT(domain) FROM sites;")
        self.domains = set([i[0] for i in self.cur.fetchall()])
        for d in self.domains:
            #search text and concat
            text = " ".join(res['words'] for res in \
                   self.mongo_db.find({"domain":d},{'words':1}))
            text = text.replace("'"," ")
            #store in postgres
            self.cur.execute('''INSERT INTO features (domain, text) VALUES('%s', '%s');'''\
                             %(d, text))
        self.con.commit()



    def fill_countries(self):
        extractcountries.run(self.con, self.engine)



    def clean_tokenized_text(self, doc, rx):
        #cleaning punctuation and non alpha content
        text = rx.sub(" ", doc).strip()
        stoplist = stopwords.words('english')
        #lemmatizing
        lemma = WordNetLemmatizer()
        split_cleaned_text = [lemma(word.lower(), pos='v') for word in text.split() if \
                       (word.isalpha() and word not in stoplist)]
        return split_cleaned_text



    def find_topics_descr_and_store(self, n_topics, n_domains):
        topicm = topic_model.topic_model()

        rx = re.compile('\W+')
        self.cur.execute("SELECT text FROM features LIMIT %d \
                          ORDER BY RAND();" %(n_domains))
        texts = []
        for row in self.cur.fetchall():
            text = clean_tokenized_text(row[0])
            texts.append(text)
        #build model on n_domains rows
        self.topics = topicm.model(texts, n_topics)
        for k, v in self.topics.iteritems():
            descr = " ".join(v)
            print k, descr
            #self.cur.execute("INSERT INTO clusters VALUES(%d, %s);",(k, descr))
        #self.con.commit()
        #run on everything for assigning clusters
        self.cur.execute("SELECT domain, text FROM features;")
        for row in self.cur.fetchall():
            domain = row[0]
            text = row[1]
            pred = topicm.predict(clean_tokenizes_text(text))
            print domain, pred
            #self.cur.execute('''UPDATE features2 SET cluster_id=%d WHERE domain='%s';'''\
            #                 %(pred, domain))
        #self.con.commit()
        model.clear()



    def similar_extract(self):
        conceptextractor.extract_and_store(self.con, self.cur, self.topics.keys())



if __name__ == '__main__':
    shal = shallots()
    
    # ADD "LANGUAGE" FIELD TO MONGODB
    #shal.add_languages_mongo(stepsize =1000, start=0)
    
    # DROP, MAKE DATABASES & TABLES POSTGRES
    #shal.make_sql_database()

    # FILL TABLES WITH REFERRALS TO MONGO ID
    # (FILTER IN ENGLISH LANGUAGE)
    #shal.fill_mongoref_sql_database()

    # EXTRACT DOMAINS FROM HTML AND STORE IN TABLE
    #shal.fill_sitesite_relations()

    # CLEAN AND CONCAT TEXT AND STORE IN TABLE
    #shal.group_text_store()

    # EXTRACT COUNTRIES AND STORE IN TABLE
    #shal.fill_countries()  #now stores in features2 without text

    # STORE CLUSTERS AND THEIR DESCRIPTION
    # PLUS STORE CLUSTER ASSIGNMENTS   
    shal.find_topics_descr_and_store(n_topics = 10, n_domains = 100)
    sys.exit()

    # WITHIN CLUSTES, DO SIMILAR CONCEPT EXTRACTION AND STORE'''
    shal.similar_extract()
    
    # CLOSE ALL THE CONNECTIONS
    shal.cur.close()
    shal.con.close()
    shal.client.close()
    shal.alchcon.close()

    # INSERT HANDWORK ANNOTATIONS FOR LEGAL/ILLEGAL CLUSTERS
    # INSERT HANDWORK NAMING OF CLUSTERS
    # AFTER THAT TIME TO VISUALIZE

