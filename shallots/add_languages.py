import pymongo
from pymongo import MongoClient
from langdetect import detect

print "add language field to the mongo db"

client = MongoClient('localhost', 27017)
db = client.scrapy

skipped = 0
stepsize = 10000
amount = 0
#batches by stepsize, use skip for next step
while amount <= db.onions.count():
    for i in db.onions.find().skip(skipped).limit(stepsize):
        amount+=1
        try:
            lang = detect(i['words'])
            db.onions.update({'_id' : i['_id']},\
                             {'$set': {'language': lang}})
            cnt[lang]+=1
        except: 
            db.onions.update({'_id' : i['_id']},\
                            {'$set': {'language': u'None'}})
    skipped+=stepsize
client.close()