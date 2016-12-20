import json

import datetime
from rePullet.logic.pullstats import *

from rePullet.logic import g



def group_gen(urluser, urlrepo):
    #a = urlpart.split('/')
    #making github great again
    userslist = []
    for pull in g.get_repo(urluser+'/'+urlrepo).get_pulls('all'):
        current_user = {'id': pull.user.login, 'content': pull.user.login}
        if current_user not in userslist:
            userslist.append(current_user)
    return json.dumps(userslist)


def items_gen(urluser, urlrepo, params):
    itemslist = []

    repo = g.get_repo(urluser + '/' + urlrepo)
    for pull in repo.get_pulls('all'):
        #проверяем, закрыт ли PR
        issue = repo.get_issue(pull.number)
        if pull.state == 'closed':
            # получаем номер
            if issue.user.login == issue.closed_by.login:
                continue  # не учитываем PR, если открывший и закрывший PR совпали
            # закрыт, смотрим автора закрытия
            if 'cl' in params:
                if issue.closed_by.login != params['cl']:
                    continue #не учитываем PR, закрытые не указанным пользователем
        # теперь узнаем количество доделок
        # сначала узнаем, нужно ли проверять на доделку
        rebuild = 0
        if pull.comments != 0:
            rebuild = count_rebuild(issue, pull)
        # теперь узнаем, содержит ли отчет о лабе (pdf, doc(x))
        report = countReport(pull)
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
    return json.dumps(itemslist)

def options_gen(urluser, urlrepo):
    options = {}
    datetimelist = []
    for pull in g.get_repo(urluser + '/' + urlrepo).get_pulls('all'):
        datetimelist.append(pull.created_at)
    options['min'] = (min(datetimelist)-datetime.timedelta(days=50)).strftime('%Y-%m-%d %H:%M')
    options['max'] = (datetime.datetime.now()+datetime.timedelta(days=50)).strftime('%Y-%m-%d %H:%M')
    options['zoomMin'] = '60000'
    options['zoomMax'] = (datetime.datetime.now()-min(datetimelist)).total_seconds() * 3000
    options['maxHeight'] = '550px'
    options['dataAttributes'] = ['rework', 'report']
    options['clickToUse'] = 'true'
    # options['type'] = 'point'
    # options['showMajorLabels'] = 'false'
    return json.dumps(options)


