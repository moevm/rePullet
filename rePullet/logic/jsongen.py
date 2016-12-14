import json

import datetime
from github import PullRequest


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
        if pull.state == 'closed':
            # получаем номер
            issue = repo.get_issue(pull.number)
            if issue.user.login == issue.closed_by.login:
                continue  # не учитываем PR, если открывший и закрывший PR совпали

            if 'cl' in params:
                if issue.closed_by.login != params['cl']:
                    continue #не учитываем PR, закрытые не указанным пользователем
            #закрыт, смотрим автора закрытия
            itemslist.append({'id': pull.id,
                              'group': pull.user.login,
                              'content': pull.title,
                              'start': pull.created_at.strftime('%Y-%m-%d %H:%M'),
                              'end': pull.closed_at.strftime('%Y-%m-%d %H:%M'),
                              'className': 'grey'})
        else:
            itemslist.append({'id': pull.id,
                              'group': pull.user.login,
                              'content': pull.title,
                              'start': pull.created_at.strftime('%Y-%m-%d %H:%M'),
                              'end': datetime.datetime.now().strftime('%Y-%m-%d %H:%M')})
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
    # options['type'] = 'point'
    # options['showMajorLabels'] = 'false'
    return json.dumps(options)
