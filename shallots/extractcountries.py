import os
import csv
import pycountry
import sqlite3
import pandas as pd
import pandas.io.sql as psql
from collections import Counter #might need that later
from fuzzywuzzy import fuzz
import geograpy2
from geograpy2.extraction import Extractor

import pymongo
from pymongo import MongoClient

from sqlalchemy import create_engine

#decicion: country = true/false instead of counts

#for every mongo_id in sql and cleaned text
#find countries in text as set

#create pandas dataframe
#put set in pandas (id, country, country, country)
#create columns in sql based on all found countries
#store pandas dataframe in sql

def correct_country_mispelling(s):
        with open("data/ISO3166ErrorDictionary2.csv", "rb") as info:
            reader = csv.reader(info)
            for row in reader:
                if fuzz.ratio(s, row[0].decode('utf-8')) > 75:
                    return row[2]

        return s

def is_a_country2(s): 
    s = correct_country_mispelling(s)
    try:
        pycountry.countries.get(name=s)
        return True
    except KeyError, e:
        return False

def get_countries(s):
    places = geograpy2.get_place_context(text=s)
    return set([correct_country_mispelling(place) for place in set(places.names)\
        if is_a_country2(correct_country_mispelling(place))])

def run(db, con, cur):
    print "extracting countries from text and storing"
    data = psql.read_sql("SELECT domain, text from features limit 10;", con)
    for index, row in data.iterrows():
        print index
        countries = get_countries(row['text'].decode('utf-8'))
        for country in countries:
            print country
            data.loc[index, country]=True
            #data[data['domain']==row['domain']][country]=True

    data = data.fillna(False)
    print data.head(10)
    #data.to_sql('features', con, if_exists='replace')

'''
    engine = create_engine('postgresql://bla:bla@localhost:1234/mydatabase')
    data['mongo_id'] = pd.read_sql_table('features', engine, index_col='mongo_id')
    
    for id in data['mongo_id']:
        text = db.onions.find({'_id': id})['words']
        countries = get_countries(text)
        for country in countries:
            data[data['mongo_id']==id][country]=True
    
    #need to check if override or new table is best
    data.to_sql('table_name', engine)'''




