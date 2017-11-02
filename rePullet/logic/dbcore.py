import datetime
import pprint

from flask import json

import rePullet.logic.ghcore as gh
from rePullet.logic import db, db_users, db_deadlines


def updateUserInfo(user):
    doc = db_users.find_one({'gitId': user.id})
    if not doc:
        db_users.insert_one({
            'gitId': user.id,
            'repos': []
        })
    return doc

def addToTrack(urlstr, user):
    """
    :param urlstr: str
    :param user: User
    :return: bool
    """
    doc = updateUserInfo(user) #получаем пользователя
    repoid = gh.getrepoid(user, urlstr)
    if repoid is not None:
        if not doc['repos']:
            #если записей не было, создаем
            db_users.find_one_and_update({'gitId': user.id}, {'$set': {'repos': [{'id': repoid}]}})
        else:
            #запись была, ищем нашу
            #TODO: не добавлять, если уже есть
            db_users.find_one_and_update({'gitId': user.id}, {'$addToSet': {'repos': {'id': repoid}}})
            #print(db_users.find_one({'gitId': user.id, 'repos': {'$in': [{'id': repoid}]}}))
        return gh.getRepoNameById(user, repoid)

def deleteTrackingRepo(user, repoId):
    doc = updateUserInfo(user)
    try:
        db_users.update({'gitId': 29598797}, {'$pull':{'repos': {'id': 76451566}}})
    except Exception:
        print ("can't detete repo")



def getuserrepos(user):
    """
    :param user: User
    :return: []
    """
    doc = updateUserInfo(user)  # получаем пользователя
    return doc['repos'] if doc else [{}]

def printdb():
    for c in db.collection_names():
        print(c)
        for doc in db[c].find():
            pprint.pprint(doc)

def loads_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return None
    return json_object

def addDeadlines(user, reponame, data):
    repoid = gh.getRepoIdByName(user, reponame)
    if not repoid:
        return json.dumps({'message': '404! Missing information!'})
    if not gh.is_colown(user, repoid):
        return json.dumps({'message': 'Wrong user permissions!'})
    deadlines = loads_json(data)
    if not deadlines:
        return json.dumps({'message': 'Wrong data format!'})
    #print('ok, start db logic')
    deadlist = []
    #TODO: mb validate dataranges
    for ind, val in enumerate(deadlines):
        deadlist.append({'id':chr(ind),
                         'phrase': val['phrase'],
                         'start': val['start'],
                         'end': val['end']
                         })
    #print(deadlist)
    db_deadlines.find_one_and_update({'repo_id': repoid},{'$set': {'dataranges': deadlist}}, upsert=True)

def getDeadlinesByName(user, reponame):
    repoid = gh.getRepoIdByName(user, reponame)
    doc = db_deadlines.find_one({'repo_id': repoid})
    return doc['dataranges'] if doc else []

def stringToColor(str):
    hash = 0
    for i in str:
        hash = ord(i) + ((hash << 5) - hash)
    colour = '#'
    for x in range(0, 3):
        v = hash >> (x*8) & 0xFF
        colour+=('00' + hex(v).lstrip('0x'))[2:]
    rgb = tuple(int(colour.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    return rgb

def checkDeadline(user, reponame, name, start, end):
    repodeadlines = getDeadlinesByName(user, reponame)
    if repodeadlines:
        for k in repodeadlines:
            if 'phrase' in k and (k['phrase'] in name):
                print(k['end'], end)
                if end and end < datetime.datetime.strptime(k['end'], '%d-%m-%Y'):
                    return True
    return False

