import pymongo
from pymongo import MongoClient
from langdetect import detect

def run(db, stepsize =1000, start=0):
    print "start running langdetect"
    skipped = 0
    amount = start
    #batches by stepsize, use skip for next step
    while amount <= db.count():
        print amount
        for i in db.find().skip(skipped).limit(stepsize):
            amount+=1
            try:
                lang = detect(i['words'])
                db.update({'_id' : i['_id']},\
                                 {'$set': {'language': lang}})
            except: 
                db.update({'_id' : i['_id']},\
                                {'$set': {'language': u'None'}})
        skipped+=stepsize
    print "finished langdetect"