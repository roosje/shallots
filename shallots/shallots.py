#class shallots(object):

import add_languages
import pymongo
from pymongo import MongoClient
from psycopg2 import connect
import psycopg2

def add_languages_mongo():
    add_languages()

def make_sql_database():
    #drop everything
    #create database
    #create tables
    setup_postgres()
    pass

def fill_mongoref_sql_database():
    #select only english
    #get mongo_id
    #store in sql
    client = MongoClient('localhost', 27017)
    db = client.scrapy
    con = connect(database='shallots', user ='postgres', password='****', host='localhost')
    cur = con.cursor()
    for i in db.onions.find({"language": "en"})['_id']
        #insert into table sites field: mongo_id
        cur.execute("INSERT INTO sites VALUES (i);")
    con.commit()
    cur.close()
    con.close()

def fill_sitesite_relations():
    pass

def fill_countries():
    pass

def clean_text():
    #remove ascii
    #lower
    #store
    pass

def tokenize_text():
    #stem
    #tokenize
    #store
    pass

def find_clusters():
    pass

def get_cluster_description():
    pass

def store_clus_desc():
    pass

def similar_extract():
    pass

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
