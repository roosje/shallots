import add_languages
import setup_postgres
import extractcountries

import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId

from psycopg2 import connect
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from sqlalchemy import Table, MetaData, create_engine

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
        self.clusters = {}
        self.domains = set()
        self.engine = create_engine("postgresql://postgres:%s@%s/%s" \
                      %(password, server, self.sql_dbname))
        self.alchcon = self.engine.connect().connection

    def add_languages_mongo(self, stepsize, start):
        add_languages.run(self.mongo_db, stepsize, start)

    def make_sql_database(self):
        #get current tables
        self.cur.execute("SELECT relname FROM pg_class WHERE relkind='r' AND \
                          relname !~ '^(pg_|sql_)';")
        tables = [i[0] for i in self.cur.fetchall()]
        #drop all tables
        for table in tables:
            setup_postgres.drop_table(self.con, self.cur, table)
        #create tables
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

    def clean_text_store(self):
        print "concat text per domain, clean and store"
        self.cur.execute("SELECT DISTINCT(domain) FROM sites;")
        self.domains = set([i[0] for i in self.cur.fetchall()])
        for d in self.domains:
            #search text and concat
            text = " ".join(res['words'] for res in \
                   self.mongo_db.find({"domain":d},{'words':1}))
            #cleaning punctuation and non alpha content
            '''
            rx = re.compile('\W+')
            text = rx.sub(" ", text).strip()
            text = " ".join([word.lower() for word in text.split() if \
                       word.isalpha()])'''
            text = text.replace("'"," ")
            #store in postgres
            self.cur.execute('''INSERT INTO features (domain, text) VALUES('%s', '%s');'''\
                             %(d, text))
        self.con.commit()

    def fill_countries(self):
        extractcountries.run(self.con, self.engine)

    def find_clusters_descr_and_store(self, n_topics):
        self.clusters = topic_model.model(data, n_topics)
        for k, v in self.clusters.iteritems():
            descr = " ".join(v)
            self.cur.execute("INSERT INTO clusters VALUES(%d, %s);",(k, descr))

    def similar_extract(self):
        conceptextractor.extract_and_store(self.con, self.cur, self.clusters)

if __name__ == '__main__':
    shal = shallots()
    '''add "language" field to mongodb'''
    #shal.add_languages_mongo(stepsize =1000, start=0)
    '''drop, make database & tables postgres'''
    #shal.make_sql_database()
    '''fill tables with referrals to mongo ID (filter on english language)'''
    #shal.fill_mongoref_sql_database()
    '''extract urls (domains) and store in table'''
    #shal.fill_sitesite_relations()
    '''clean and concat text and store in sql'''
    #shal.clean_text_store()
    '''extract countries and store in table'''
    shal.fill_countries()  #now stores in features2
    '''store clusters and their description'''
    #shal.find_clusters_descr_and_store(n_topics = 10)
    sys.exit()
    '''handwork annotating legal/illegal'''
    '''within clusters, do similar concept extraction and store in table'''
    shal.similar_extract()
    '''visualize (tell flask to prepare everything)'''
    shal.cur.close()
    shal.con.close()
    shal.client.close()
    shal.alchcon.close()