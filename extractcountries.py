import os
import csv
import pycountry
import pandas as pd
from fuzzywuzzy import fuzz
import geograpy2
from geograpy2.extraction import Extractor

import pymongo
from pymongo import MongoClient

import pandas.io.sql as psql

'''
These functions help with extracting the countries from the text
-geograpy2 uses nltk for entity extraction
-the countrydict in combination with fuzzywuzzy is used to correct spelling
errors and synonyms
-pycountry is used to check if the string is known as a country
I made the decision at this point to use true/false instead of counts per doc
'''


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
    return set([pycountry.countries.get(name=correct_country_mispelling(place))
                .alpha3 for place in set(places.names)
                if is_a_country2(place)])


def run(conn, engine):
    print "extracting countries from text and storing"
    try:
        data = pd.read_pickle('data/countries.pkl')
    except:
        data = psql.read_sql("SELECT domain, text FROM features;", engine)
        for index, row in data.iterrows():
            if len(row['text']) > 0:
                countries = get_countries(
                    row['text'].encode('utf-8').decode('utf-8'))
                for country in countries:
                    data.loc[index, country] = True
        data = data.fillna(False)
        data.pop('text')
        data.to_pickle('data/countries.pkl')

    psql.to_sql(data, "countries", con=engine, if_exists='replace',
                index=False)
