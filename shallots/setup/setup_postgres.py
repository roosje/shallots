#create database
from psycopg2 import connect
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

con=None
cur=None

def show_databases():
    cur.execute('''SELECT datname from pg_database''')
    databases = cur.fetchall()
    print databases

def create_database(dbname):
    try:
        cur.execute('CREATE DATABASE ' + dbname)
        con.commit()
    except psycopg2.Error as e:
        print e

def drop_table(tablename):
    cur.execute("DROP TABLE IF EXISTS " + tablename)
    con.comit()

def create_tables():
    #create table sites    
    cur.execute("SELECT exists(SELECT * FROM information_schema.tables WHERE table_name=%s)", \
                ('sites',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE sites (site_id SERIAL PRIMARY KEY, mongo_id INTEGER);")
    #create table features 
    #!!!!!----------need to change to 1 column per extracted country----!!!!
    cur.execute("SELECT exists(SELECT * FROM information_schema.tables WHERE table_name=%s)", \
                ('features',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE features (site_id INTEGER, cluster_id INTEGER, countries VARCHAR);")
    #create table clusters    
    cur.execute("SELECT exists(SELECT * FROM information_schema.tables WHERE table_name=%s)", \
                ('clusters',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE clusters (cluster_id INTEGER, cluster_name VARCHAR, \
                    legal BOOLEAN, description VARCHAR);")
    #create table relations    
    cur.execute("SELECT exists(SELECT * FROM information_schema.tables WHERE table_name=%s)", \
                ('relations',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE relations (site_id_from INTEGER, site_id_to INTEGER);")
    #create table clusterwordvecs    
    cur.execute("SELECT exists(SELECT * FROM information_schema.tables WHERE table_name=%s)", \
                ('clusterwordvecs',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE clusterwordvecs (cluster_id INTEGER, \
                    word_1 VARCHAR, word_2 VARCHAR, simscore REAL);")
    con.commit()
    
def main():
    dbname= 'shallots'
    con = connect(database='shallots', user ='postgres', password='****', host='localhost')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    tables = #@@@
    #drop all tables
    for table in tables:
        drop_table(table)
    #create tables
    create_tables()
    #close connections
    cur.close()
    con.close()

if __name__ == '__main__':
    main()

