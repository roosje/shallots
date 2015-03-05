import pymongo
from pymongo import MongoClient
from langdetect import detect

def run(db):
    skipped = 0
    stepsize = 10000
    amount = 0
    #batches by stepsize, use skip for next step
    while amount <= db.count():
        for i in db.find().skip(skipped).limit(stepsize):
            amount+=1
            try:
                lang = detect(i['words'])
                db.update({'_id' : i['_id']},\
                                 {'$set': {'language': lang}})
                cnt[lang]+=1
            except: 
                db.update({'_id' : i['_id']},\
                                {'$set': {'language': u'None'}})
        skipped+=stepsize