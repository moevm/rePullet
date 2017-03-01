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

def items_gen(user, urluser, urlrepo):
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
                # # закрыт, смотрим автора закрытия
                # if 'cl' in params:
                #     if issue.closed_by.login != params['cl']:
                #         continue  # не учитываем PR, закрытые не указанным пользователем
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
                rgb = db.stringToColor(datarange['phrase'])
                itemslist.append({'id': datarange['id'],
                                  'start': datetime.datetime.strptime(
                                      datarange['start'], '%d-%m-%Y').strftime('%Y-%m-%d %H:%M'),
                                  'end': datetime.datetime.strptime(
                                      datarange['end'], '%d-%m-%Y').strftime('%Y-%m-%d %H:%M'),
                                  'type': 'background',
                                  'content': datarange['phrase'],
                                  'isback': '0',
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
        options['zoomMax'] = (datetime.datetime.now() - a).total_seconds() * 10000
        options['height'] = '500px'
        options['verticalScroll'] = True
        options['maxHeight'] = '500px'
        options['dataAttributes'] = ['rework', 'report', 'isback']
        options['clickToUse'] = True
        # options['type'] = 'point'
        # options['showMajorLabels'] = 'false'
        return json.dumps(options)
    except:
        # TODO: split exceptions
        return json.dumps({'message': 'Exception for some reason!'})


def rating_gen(user, urluser, urlrepo):
    try:
        reponame = urluser + '/' + urlrepo
        repo = user.ghI.get_repo(reponame)
        students = {}
        if repo:
            for pull in repo.get_pulls('all'):
                issue = repo.get_issue(pull.number)
                author_id = pull.user.id
                if author_id not in students:
                    login = pull.user.login
                    fullname = getUserName(user, login)
                    url = pull.user.html_url
                    students[author_id] = {'_id': author_id,
                                           'login': login,
                                           'full_name': fullname,
                                           'url': url,
                                           'opened': 0,
                                           'intime': 0,
                                           'delay': 0,
                                           'closed': 0,
                                           'rework': 0}
                student = students[author_id]
                #update info
                student['opened'] += 1
                if pull.state == 'closed':
                    if issue.user.login == issue.closed_by.login:
                        continue  # не учитываем PR, если открывший и закрывший PR совпали
                    student['closed'] += 1
                    if True:
                        student['intime'] += 1
                    else:
                        student['delay'] += 1
                rebuild = count_rebuild(issue, pull)  # считаем количество доработок
                #print('reb = ', rebuild)
                student['rework'] += rebuild
                #print(student)
        #print(students)
        return json.dumps(students)
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