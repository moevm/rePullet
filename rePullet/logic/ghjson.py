import datetime
import json

from flask import g
from flask import jsonify

import rePullet.logic.dbcore as db
from rePullet.logic.ghcore import *


def group_gen(urluser, urlrepo):
    try:
        repo = g.user.ghI.get_repo(urluser+ '/' + urlrepo)
        userslist = []
        for pull in repo.get_pulls('all'):
            current_user = {'id': pull.user.login, 'content': pull.user.login}
            if current_user not in userslist:
                userslist.append(current_user)
        return json.dumps(userslist)
    except:
        #TODO: split exceptions
        return json.dumps({'message': 'Exception for some reason!'})

def items_gen(user, urluser, urlrepo, params):
        reponame = urluser + '/' + urlrepo
        repo = user.ghI.get_repo(reponame)
        itemslist = []
        for pull in repo.get_pulls('all'):
            # проверяем, закрыт ли PR
            issue = repo.get_issue(pull.number)
            if pull.state == 'closed':
                # получаем номер
                if issue.user.login == issue.closed_by.login:
                    continue  # не учитываем PR, если открывший и закрывший PR совпали
                # закрыт, смотрим автора закрытия
                if 'cl' in params:
                    if issue.closed_by.login != params['cl']:
                        continue  # не учитываем PR, закрытые не указанным пользователем
            rebuild = count_rebuild(issue, pull) #считаем количество доработок
            report = countReport(pull)  # теперь узнаем, содержит ли PR отчет о лабе (pdf, doc(x))
            if pull.state == 'closed':
                itemslist.append({'id': pull.id,
                                  'group': pull.user.login,
                                  'content': pull.title,
                                  'start': pull.created_at.strftime('%Y-%m-%d %H:%M'),
                                  'end': pull.closed_at.strftime('%Y-%m-%d %H:%M'),
                                  'className': 'grey',
                                  'rework': rebuild,
                                  'report': report})
            else:
                itemslist.append({'id': pull.id,
                                  'group': pull.user.login,
                                  'content': pull.title,
                                  'start': pull.created_at.strftime('%Y-%m-%d %H:%M'),
                                  'end': datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                                  'rework': rebuild,
                                  'report': report})
        #deadline improvements!
        dataranges = db.getDeadlinesByName(user, reponame)
        for datarange in dataranges:
            print(datarange)
            if datarange:
                rgb = db.stringToColor('lold')
                itemslist.append({'id': datarange['id'],
                                  'start': datetime.datetime.strptime(
                                      datarange['start'], '%d-%m-%Y').strftime('%Y-%m-%d %H:%M'),
                                  'end': datetime.datetime.strptime(
                                      datarange['end'], '%d-%m-%Y').strftime('%Y-%m-%d %H:%M'),
                                  'type': 'background',
                                  'content': 'lold',
                                  'style': 'background-color:rgba('
                                           ''+str(rgb[0])+','+str(rgb[1])+','+str(rgb[2])+', 0.2);'
            })
        print(itemslist)
        return json.dumps(itemslist)


def options_gen(urluser, urlrepo):
    try:
        options = {}
        datetimelist = []
        for pull in g.user.ghI.get_repo(urluser + '/' + urlrepo).get_pulls('all'):
            datetimelist.append(pull.created_at)
        a = datetime.datetime.now() - datetime.timedelta(days=50)
        if datetimelist:
            a = min(datetimelist)
        options['min'] = (a- datetime.timedelta(days=50)).strftime('%Y-%m-%d %H:%M')
        options['max'] = (datetime.datetime.now() + datetime.timedelta(days=50)).strftime('%Y-%m-%d %H:%M')
        options['zoomMin'] = 60000
        options['zoomMax'] = (datetime.datetime.now() - a).total_seconds() * 3000
        options['maxHeight'] = '550px'
        options['dataAttributes'] = ['rework', 'report']
        options['clickToUse'] = True
        # options['type'] = 'point'
        # options['showMajorLabels'] = 'false'
        return json.dumps(options)
    except:
        # TODO: split exceptions
        return json.dumps({'message': 'Exception for some reason!'})


def user_gen():
    return jsonify(str(g.user))
    # k = noUser(g.user.ghI)
    # if k:
    #     return k
    # print(g.user.ghI.get_user().login)
    # return jsonify(g.user.ghI.get_user().login)


def date_gen(request_data):
    print(jsonify(request_data))
    return jsonify(request_data)


def noUser(user):
    return jsonify({"message": "Need to github authentication first!"}) if user is None else False

def userrepos_json(user):
    a = db.getuserrepos(user) #repo list from db
    for i in a:
        repo = user.ghI.get_repo(i['id'])
        if repo:
            i['fullname'] = repo.full_name
            i['owner'] = repo.owner.name
            i['name'] = repo.name
        else:
            a.remove(i)
    return json.dumps(a)