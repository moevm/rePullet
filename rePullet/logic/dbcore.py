import pprint

from flask import json

import rePullet.logic.ghcore as gh
from rePullet.logic import db, db_users, db_deadlines


def saveDates(jsondata, user, urluser, urlrepo):
    if not jsondata:
        jsondata = []
    #начинаем с записи о репозитории
    #смотрим, есть ли запись
    doc = db_users.find_one({'gitId': user.id})
    if not doc['repos']: #если записей не было, создаем
        print(doc['repos'])
        db_users.find_one_and_update({'gitId': user.id}, {'$set': {'repos': [{'name':urluser+'/'+urlrepo, 'dates': jsondata}]}})
    else:
        # записи были, ищем нашу
        doc = db_users.find_one_and_update({'gitId': user.id, 'repos.name': urluser+'/'+urlrepo},{'$set':{'repos.$.dates': jsondata}})
        if not doc:
            db_users.find_one_and_update({'gitId': user.id},{'$addToSet': {'repos': [{'name': urluser + '/' + urlrepo, 'dates': jsondata}]}})
        #doc['repos']['dates'] = jsondata
        #db_users.update_one
        # и если ее не было, добавим
        #db_users.update_one({'gitId': user.id} , {'$push': {'repos': {'name': urluser+'/'+urlrepo, 'dates': jsondata}}})

def loadDates():
    pass

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
    return doc['dataranges'] if doc else [{}]

def stringToColor(str):
    hash = 0
    for i in str:
        hash = ord(i) + ((hash << 5) - hash)
    colour = '#'
    for x in range(0, 3):
        v = hash >> (x*8) & 0xFF
        colour+=('00' + hex(v).lstrip('0x'))[2:]
    #print(colour)
    rgb = tuple(int(colour.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    return rgb
    #return colour

def checkDeadline(user, reponame, name, start, end):
    repodeadlines = getDeadlinesByName(user, reponame)
    for k in repodeadlines:
        #print(k)
        if k['phrase'] in name:
            #print(k['phrase'], name)
            if end < k['end']:
                #print(end)
                return True
    return False

