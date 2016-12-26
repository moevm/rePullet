from rePullet.logic import db, db_deadline, db_users


def saveDates(jsondata, user, urluser, urlrepo):
    print(jsondata)
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
            db_users.find_one_and_update({'gitId': user.id},{'$push': {'repos': [{'name': urluser + '/' + urlrepo, 'dates': jsondata}]}})
        #doc['repos']['dates'] = jsondata
        #db_users.update_one
        # и если ее не было, добавим
        #db_users.update_one({'gitId': user.id} , {'$push': {'repos': {'name': urluser+'/'+urlrepo, 'dates': jsondata}}})



def updateUserInfo(user):
    db_users.update_one({'gitId': user.id}, {'$set': {'gitName': user.name, 'repos': []}}, upsert=True)