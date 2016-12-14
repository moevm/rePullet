import json

import datetime

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


def items_gen(urluser, urlrepo):
    itemslist = []
    for pull in g.get_repo(urluser + '/' + urlrepo).get_pulls('all'):
        itemslist.append({'id': pull.id,
                          'group': pull.user.login,
                          'content': pull.title,
                          'start': pull.created_at.strftime('%Y-%m-%d %H:%M')})
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
