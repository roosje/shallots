import add_languages
import setup_postgres

import pymongo
from pymongo import MongoClient

from psycopg2 import connect
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class shallots(object):
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.dbname= 'shallots'
        self.db = self.client.scrapy.onions
        self.con = connect(database='shallots', user ='postgres', password='****', host='localhost')
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.con.cursor()
        self.clusters = {}
        self.comains =[]

    def add_languages_mongo(self, stepsize, start):
        add_languages.run(self.db, stepsize, start)

    def make_sql_database(self):
        #create database ?
        #create tables
        tables = #@@@
        #drop all tables
        for table in tables:
            setup_postgres.drop_table(self.con, self.cur, table)
        #create tables
        setup_postgres.create_tables(self.con, self.cur)

    def fill_mongoref_sql_database(self):
        #select only english
        #get mongo_id
        #store in sql
        for i, d in self.db.find({"language": "en"})['_id', 'domain']
            self.domains.append(d)
            #insert into sites fields: mongo_id and domain, site_id is serial
            self.cur.execute("INSERT INTO sites VALUES (%s, %s);", (i, d))
        self.con.commit()
        
    def fill_sitesite_relations(self):
        for d in self.domains:
            #get html from mongo for that domain
            html = self.db.find({"domain": d}['HTML'])
            #find domains in htmls
            #store d, domains in relations
        self.con.commit()    

    def fill_countries(self):
        extractcountries.run(self.client)

    def clean_text_store():
        #group text per domain get from mongo
        self.cur.execute("SELECT DISTINCT(domain) FROM sites;")
        domains = self.cur.fetchall()
        for d in domains:
            text = " ".join(db.find({"domain":d})['words'].values)
            #remove ascii
            text = text.lower()
            #store in postgres
            self.cur.execute("INSERT INTO features VALUES(%s, %s);", (d, text))
        self.con.commit()

    def find_clusters_descr_and_store(self, n_topics):
        self.clusters = topic_model.model(data, n_topics)
        for k, v in self.clusters.iteritems():
            descr = " ".join(v)
            self.cur.execute("INSERT INTO clusters VALUES(%d, %s);",(k, descr))

    def similar_extract(self):
        conceptextractor.extract_and store(self.con, self.cur, self.clusters)

if __name__ == '__main__':
    #shal = shallots()
    #add "language" field to mongodb
    self.add_languages_mongo(stepsize =100, start=0)
    break
    #drop, make database & tables postgres
    self.make_sql_database()
    #fill tables with referrals to mongo ID (filter on english language)
    self.fill_mongoref_sql_database()
    #extract urls (domains) and store in table
    self.fill_sitesite_relations()
    #clean and concat text and store in sql
    self.clean_text_store()
    #extract countries and store in table
    self.fill_countries()
    #store clusters and their description
    self.find_clusters_descr_and_store(n_topics = 10)
    '''handwork annotating legal/illegal'''
    #within clusters, do similar concept extraction and store in table
    self.similar_extract()
    #visualize (tell flask to prepare everything)
    self.cur.close()
    self.con.close()
    self.client.close()