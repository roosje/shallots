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
    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('sites',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE sites (site_id serial PRIMARY KEY, mongo_id integer);")
    #create table features 
    #!!!!!----------need to change to 1 column per extracted country----!!!!
    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('features',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE features (site_id integer, cluster_id integer, countries varchar);")
    #create table clusters    
    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('clusters',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE clusters (cluster_id integer, cluster_name varchar, \
                    legal boolean, description varchar);")
    #create table relations    
    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('relations',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE relations (site_id_from integer, site_id_to integer);")
    #create table clusterwordvecs    
    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('clusterwordvecs',))
    if not cur.fetchone()[0]:
        cur.execute("CREATE TABLE clusterwordvecs (cluster_id integer, \
                    word_1 varchar, word_2 varchar, simscore real);")
    con.commit()
    

if __name__ == '__main__':
    dbname= 'shallots'
    con = connect(database='shallots', user ='postgres', password='****', host='localhost')
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = con.cursor()
    #drop tables
    #drop_table('clusters')
    #create tables
    create_tables()
    #close connections
    cur.close()
    con.close()
