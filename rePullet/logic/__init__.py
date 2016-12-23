from config import Config as c
from pymongo import MongoClient
from github import Github

class Ins:
    gt = None
    dbinstance = MongoClient(c.MONGOHOST, c.MONGOPORT)[c.MONGONAME]