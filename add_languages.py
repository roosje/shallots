import pymongo
from pymongo import MongoClient
from langdetect import detect

def run(db, stepsize =1000, start=0):
    '''
    INPUT: mongo db, int, int
    OUTPUT: -

    Connects to all documents in MongoClient. 
    Detects the language of the "words" field.
    Stores language as new field in same Mongo (none if unknown)
    '''

    print "start running langdetect"
    skipped = 0
    amount = start
    # BATCHES BY STEPSIZE, USE SKIP FOR NEXT STEP
    while amount <= db.count():
        print amount
        for i in db.find().skip(skipped).limit(stepsize):
            amount += 1
            try:
                lang = detect(i['words'])
                db.update({'_id' : i['_id']},\
                                 {'$set': {'language': lang}})
            except: # LANGDETECT THROWS ERROR (TEXT TOO SHORT)
                db.update({'_id' : i['_id']},\
                                {'$set': {'language': u'None'}})
        skipped += stepsize
    print "finished langdetect"