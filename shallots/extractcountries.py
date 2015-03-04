import os
import csv
import pycountry
import sqlite3
from collections import Counter #might need that later
from fuzzywuzzy import fuzz
import geograpy2
from geograpy2.extraction import Extractor


url = 'http://wikitravel.org/en/europe'
'''e = Extractor(url=url)
e.find_entities()
print e.places
print "--------------------------------------"'''
places = geograpy2.get_place_context(url=url)
print places.names

def correct_country_mispelling(s):
        with open("data/ISO3166ErrorDictionary.csv", "rb") as info:
            reader = csv.reader(info)
            for row in reader:
                if fuzz.ratio(s, row[0].decode('utf-8')) > 75:
                #if s in row[0].decode('utf-8'):
                    return row[2]

        return s

def is_a_country2(s): 
    s = correct_country_mispelling(s)
    try:
        pycountry.countries.get(name=s)
        return True
    except KeyError, e:
        return False

countries = set([correct_country_mispelling(place) for place in set(places.names) if is_a_country2(place)])