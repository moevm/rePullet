import json

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
                          'start': pull.created_at.strftime('%Y-%m-%d')})
    return json.dumps(itemslist)