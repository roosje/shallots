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
        self.mongo_db = self.client.shallots.onions
        self.sql_dbname= 'shallots'
        self.con = connect(database=self.sql_dbname, user ='postgres', \
                           password=password, host=server)
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.con.cursor()
        self.n_topics = 15
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


    def find_topics_descr_and_store(self, n_topics, n_domains):
        topicm = topic_model.topic_model()

        rx = re.compile('\W+')
        self.cur.execute("SELECT text FROM features \
                          ORDER BY RANDOM() \
                          LIMIT %d;" %(n_domains))
        texts = []
        for row in self.cur.fetchall():
            text = clean_tokenized_text(row[0], rx)
            texts.append(text)
        #build model on n_domains rows
        tpcs = topicm.model(texts, n_topics)
        for k, v in tpcs.iteritems():
            # add 1 to cluster id to not have cluster with nr 0
            descr = " ".join(v)
            print k, descr
            self.cur.execute("INSERT INTO clusters (cluster_id, description) \
                              VALUES(%d, '%s');" %(k+1, descr))
        self.con.commit()

        #run on everything for assigning clusters
        self.cur.execute("SELECT domain, text FROM features;")
        for row in self.cur.fetchall():
            domain = row[0]
            text = clean_tokenized_text(row[1], rx)
            pred = topicm.predict(text)
            #print domain, pred
            self.cur.execute('''UPDATE features SET cluster_id=%d WHERE domain='%s';'''\
                             %(pred+1, domain))
        self.con.commit()


    def similar_extract(self):
        topics = range(1, self.n_topics + 1)
        conceptextractor.extract_and_store(self.con, self.cur, topics)

    def prepare_for_web(self):
        # CODE FOR WORDCLOUD 
        rx = re.compile('\W+')  
        data = psql.read_sql("SELECT cluster_id-1 AS cluster, text FROM features;", engine)
        data['text'] = data['text'].apply(lambda x: (clean_tokenized_text(x, rx)))
        data = data.groupby('cluster')['text'].apply(lambda x: \
                        list(itertools.chain.from_iterable(x))).reset_index()
        for i, row in data.iterrows():
            filename = 'web/static/data/worddata'+str(i)+'.csv'
            pd.Series(row['text']).to_csv(filename, index=False)


        # CODE FOR GRAPH DOMAIN BASED
        dataNodes = psql.read_sql("SELECT cluster_id-1 as index2, domain \
                        FROM features", engine)
        dataNodes['group'] = pd.Series(np.random.randint(1,16, size=len(dataNodes)))
        dataNodes['size'] = pd.Series(np.random.randint(1, 101, size=len(dataNodes)))
        dataNodes['index'] = dataNodes.index
        dataNodes = dataNodes.set_index('domain')
        dataLinks = psql.read_sql("SELECT * FROM relations;", engine)
        dataLinks['value']= pd.Series(np.random.randint(1, 6, size=len(dataLinks)))
        dataLinks = dataLinks.join(dataNodes['index'], on='domain_from')
        dataLinks.rename(columns={'index':'source'}, inplace=True)
        dataLinks = dataLinks.join(dataNodes['index'], on='domain_to')
        dataLinks.rename(columns={'index':'target'}, inplace=True)
        dataNodes = dataNodes.reset_index()
        dataNodes.to_json('web/static/data/nodes.json', orient="records")
        dataLinks.to_json('web/static/data/links.json', orient="records")

        # CODE FOR GRAPH TOPIC BASED
        dataNodes2 = psql.read_sql('''SELECT clusters.cluster_id-1 AS tmp, size, \
                                cluster_name AS name \
                                FROM clusters JOIN \
                                (SELECT cluster_id, \
                                count(*) as size FROM features \
                                GROUP BY cluster_id) AS cl \
                                ON clusters.cluster_id = cl.cluster_id;''', engine)
        dataNodes2['index'] = dataNodes2.index
        dataNodes2.rename(columns={'tmp':'group'}, inplace=True)
        dataNodes2 = dataNodes2.set_index('group')
        dataLinks2 = psql.read_sql("SELECT cluster_id-1 AS cluster_to, cluster_from, \
                                    COUNT(*) AS value \
                                    FROM features JOIN \
                                    (SELECT cluster_id-1 AS cluster_from, domain_to \
                                    FROM features JOIN relations \
                                    ON relations.domain_from = features.domain) AS prt1 \
                                    ON prt1.domain_to = features.domain \
                                    WHERE cluster_id-1 <> cluster_from \
                                    GROUP BY cluster_to, cluster_from;", engine)
        dataLinks2 = dataLinks2.join(dataNodes2['index'], on='cluster_from')
        dataLinks2.rename(columns={'index':'source'}, inplace=True)
        dataLinks2 = dataLinks2.join(dataNodes2['index'], on='cluster_to')
        dataLinks2.rename(columns={'index':'target'}, inplace=True)
        dataNodes2 = dataNodes2.reset_index()
        dataNodes2.to_json('web/static/data/nodes2.json', orient="records")
        dataLinks2.to_json('web/static/data/links2.json', orient="records")




if __name__ == '__main__':
    print "starting pipeline"
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

    # REMOVE THIS FILE TO START OVER WITH EXTRACTING COUNTRIES
    #os.remove('data/countries.pkl')
    
    # EXTRACT COUNTRIES AND STORE IN TABLE
    #shal.fill_countries() 

    # STORE CLUSTERS AND THEIR DESCRIPTION
    # PLUS STORE CLUSTER ASSIGNMENTS  
    #shal.cur.execute("DELETE FROM clusters WHERE true;")
    #shal.con.commit() 
    #shal.find_topics_descr_and_store(n_topics = shal.n_topics, n_domains = 400)

    # WITHIN CLUSTES, DO SIMILAR CONCEPT EXTRACTION AND STORE
    #shal.cur.execute("DELETE FROM clusterwordvecs WHERE true;")
    #shal.con.commit() 
    #shal.similar_extract()

    shal.prepare_for_web() 
    
    # CLOSE ALL THE CONNECTIONS
    shal.cur.close()
    shal.con.close()
    shal.client.close()
    shal.alchcon.close()

    # INSERT HANDWORK ANNOTATIONS FOR LEGAL/ILLEGAL CLUSTERS
    # INSERT HANDWORK NAMING OF CLUSTERS
    # AFTER THAT TIME TO VISUALIZE

