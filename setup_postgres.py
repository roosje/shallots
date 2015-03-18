from psycopg2 import connect
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def show_databases(con, cur):
    cur.execute('''SELECT datname from pg_database''')
    databases = cur.fetchall()
    print databases


def create_database(con, cur, dbname):
    try:
        cur.execute('CREATE DATABASE ' + dbname)
        con.commit()
    except psycopg2.Error as e:
        print e


def drop_table(con, cur, tablename):
    print "dropping: " + tablename
    cur.execute("DROP TABLE IF EXISTS " + tablename)
    con.commit()


def create_tables(con, cur):
    print "creating tables"
    # CREATE TABLE SITES
    cur.execute("CREATE TABLE sites (site_id SERIAL PRIMARY KEY, \
                 mongo_id VARCHAR(30), domain VARCHAR(25));")

    # CREATE TABLE FEATURES
    cur.execute("CREATE TABLE features (domain VARCHAR(25), text TEXT, \
                 cluster_id INTEGER);")

    # CREATE TABLE CLUSTERS
    cur.execute("CREATE TABLE clusters (cluster_id INTEGER, cluster_name VARCHAR, \
                 legal BOOLEAN, description VARCHAR(100));")

    # CREATE TABLE RELATIONS
    cur.execute("CREATE TABLE relations (domain_from VARCHAR(25), \
                 domain_to VARCHAR(25));")

    # CREATE TABLE CLUSTERWORDVECS
    cur.execute("CREATE TABLE clusterwordvecs (cluster_id INTEGER, \
                 word_1 VARCHAR(50), word_2 VARCHAR(50), simscore REAL);")
    con.commit()
