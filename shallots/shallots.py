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
        self.con = connect(database='shallots', user ='postgres', password='****', host='localhost')
        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cur = self.con.cursor()
        self.clusters = []

    def add_languages_mongo(self):
        add_languages(self.client)

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
        db = client.scrapy
        for i, d in db.onions.find({"language": "en"})['_id', 'domain']
            #insert into table sites field: mongo_id
            cur.execute("INSERT INTO sites VALUES (i, d);")
        self.con.commit()
        
    def fill_sitesite_relations(self):
        pass

    def fill_countries(self):
        pass

    def clean_text(self):
        #remove ascii
        #lower
        #store
        pass

    def tokenize_text(self):
        #stem
        #tokenize
        #store
        pass

    def find_clusters(self):
        self.clusters = 

    def get_cluster_description(self):
        pass

    def store_clus_desc(self):
        pass

    def similar_extract(self):
        conceptextractor(self.con, self.cur, self.clusters)

if __name__ == '__main__':
    #shal = shallots()
    #add "language" field to mongodb
    add_languages_mongo()
    #drop, make database & tables postgres
    make_sql_database()
    #fill tables with referrals to mongo ID (filter on english language)
    fill_mongoref_sql_database()
    #extract urls (domains) and store in table
    fill_sitesite_relations()
    #clean text and store in sql
    clean_text()
    #extract countries and store in table
    fill_countries()
    #tokenize and cluster
    tokenize_text()
    find_clusters()
    #get description
    get_cluster_description()
    #store clusters and their description
    store_clus_desc
    '''handwork annotating legal/illegal'''
    #within clusters, do similar concept extraction and store in table
    similar_extract()
    #visualize (tell flask to prepare everything)
    self.cur.close()
    self.con.close()