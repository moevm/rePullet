from rePullet.logic import db, db_deadline, db_users
from rePullet.logic.user import User
from urllib.parse import urlparse
import os.path
import rePullet.logic.ghcore as gh

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
            db_users.find_one_and_update({'gitId': user.id}, {'$addToSet': {'repos': {'id': repoid}}})
            #print(db_users.find_one({'gitId': user.id, 'repos': {'$in': [{'id': repoid}]}}))


def getuserrepos(user):
    """
    :param user: User
    :return: []
    """
    doc = updateUserInfo(user)  # получаем пользователя
    return doc['repos'] if doc else [{}]