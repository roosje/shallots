import os
import csv
import pycountry
import sqlite3
import pandas as pd
from collections import Counter #might need that later
from fuzzywuzzy import fuzz
import geograpy2
from geograpy2.extraction import Extractor

import pymongo
from pymongo import MongoClient

import pandas.io.sql as psql

from sqlalchemy import create_engine

import unicodedata as ud

#decicion: country = true/false instead of counts

#for every mongo_id in sql and cleaned text
#find countries in text as set

#create pandas dataframe
#put set in pandas (id, country, country, country)
#create columns in sql based on all found countries
#store pandas dataframe in sql

def correct_country_mispelling(s):

    with open("data/countrydict.csv", "rb") as info:
        reader = csv.reader(info)
        for row in reader:
            matching = row[0].decode('utf-8').lower()
            if matching == s.lower():
                return row[2]
            if fuzz.ratio(s.lower(), matching) > 80:
                return row[2]
    return s

def is_a_country2(s): 
    s = s.encode('utf-8').decode('utf-8')
    s = correct_country_mispelling(s)
    try:
        pycountry.countries.get(name=s)
        return True
    except KeyError, e:
        return False

def get_countries(s):
    places = geograpy2.get_place_context(text=s)
    return set([correct_country_mispelling(place)\
            .replace("(","").replace(")","") \
            for place in set(places.names)\
            if is_a_country2(place)])

def run(conn, engine):
    print "extracting countries from text and storing"
    try:
        data = pd.read_pickle('data/countries.pkl')
    except:
        data = psql.read_sql("SELECT domain, text FROM features;", engine)
        for index, row in data.iterrows():
            countries = get_countries(row['text'].encode('utf-8').decode('utf-8'))
            for country in countries:
                data.loc[index, country]=True

        data = data.fillna(False)
        data.pop('text')
        data.to_pickle('data/countries.pkl')

    print data.columns 
    psql.to_sql(data, "countries", con=engine, if_exists='replace', index=False)






