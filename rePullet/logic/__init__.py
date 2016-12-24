from pymongo import MongoClient

from config import Config as c


class Init:
    dbinstance = MongoClient(c.MONGOHOST, c.MONGOPORT)[c.MONGONAME]
