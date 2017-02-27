from pymongo import MongoClient

from config import Config as c

db = MongoClient(c.MONGOHOST, c.MONGOPORT)[c.MONGONAME]

db_users = db.users
db_deadlines = db['deadlines']

