from flask import redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth

from rePullet import app, login_manager
from rePullet.logic.ghjson import *

oauth = OAuth()
gh = oauth.remote_app(
    'github',
    request_token_params={'scope': 'user:email'},
    # consumer_key='a11a1bda412d928fb39a',
    # consumer_secret='92b7cf30bc42c49d589a10372c3f9ff3bb310037',
    # request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    app_key='GITHUB'
)

#
# non user routes
#

@app.before_request
def before_request():
    g.user = current_user

@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user is not None and g.user.is_authenticated:
        return render_template('index.html', user=g.user)
    else:
        return render_template('index.html', user=None)


@app.route('/how-to-pullet', methods=['GET', 'POST'])
def guide():
    return app.send_static_file('Pullet.pdf')



#
# dashboard group routes
#

@app.route('/dashboard', defaults={'ending': None}, methods=['GET', 'POST']) # remember trailing slash, BITCH
@app.route('/dashboard/<path:ending>', methods=['GET', 'POST'])
@login_required
def go_dash(ending):
    """
    :param ending:
     None = table
     new = add
     preview = ????
    :return:
    """
    url = ''
    if session.get('url'):
        url = session['url']
        session.pop('url', None)
    if request.form.get('url'): #переход по репозиторию с главной страницы
        url = request.form.get('url')
    if url != '':
        #print(url)
        repo_name = db.addToTrack(url, g.user) #добавление репозитория в список отслеживаемых
        #db.printdb()
        return redirect(url_for('go_view', ending=repo_name))
    return render_template('dashboard.html', user=g.user, path=ending)


@app.route('/view', defaults={'ending': None}, methods=['GET'])
@app.route('/view/<path:ending>', methods=['GET'])
@login_required
def go_view(ending):
    if ending is None:
        return redirect(url_for('go_dash', ending=None))
    collaborator = is_colown(g.user, ending)
    return render_template('dashboard.html', user=g.user, path='view', r=ending, access=collaborator)


@app.route('/api/groups/<urluser>/<urlrepo>', defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/<path:ending>')
@login_required
def get_groups(urluser, urlrepo, ending):
    return group_gen(urluser, urlrepo)


@app.route('/api/items/<urluser>/<urlrepo>', defaults={'ending': None}, methods=['GET', 'POST'])
@app.route('/api/items/<urluser>/<urlrepo>/<path:ending>', methods=['GET', 'POST'])
@login_required
def get_items(urluser, urlrepo, ending):
    if request.method == 'POST':
        db.addDeadlines(g.user, urluser+'/'+urlrepo, request.form['data'])
        return json.dumps(db.getDeadlinesByName(g.user, urluser+'/'+urlrepo))
    return items_gen(g.user, urluser, urlrepo)


@app.route('/api/options/<urluser>/<urlrepo>', defaults={'ending': None})
@app.route('/api/options/<urluser>/<urlrepo>/<path:ending>')
@login_required
def get_options(urluser, urlrepo, ending):
    return options_gen(g.user, urluser, urlrepo)


@app.route('/api/rating/<urluser>/<urlrepo>', defaults={'ending': None})
@app.route('/api/rating/<urluser>/<urlrepo>/<path:ending>')
@login_required
def get_rating(urluser, urlrepo, ending):
    return rating_gen(g.user, urluser, urlrepo)


@app.route('/api/addrepo', methods=['POST'])
@login_required
def post_addrepo():
    # TODO: Method not allowed
    if request.form.get('url'):
        db.addToTrack(request.form.get('url'), g.user)  # добавляем репозиторий к отслеживаемым
        return redirect(url_for('go_dash', ending=None))
    return redirect(url_for('go_dash', ending=None))

@app.route('/api/delete', methods=['POST'])
@login_required
def delete_repo():
    a = db.getuserrepos(g.user)
    checked = request.form.getlist("check")
    for todelete in checked:
        for repo in a:
            if str(todelete) == str(repo['id']):
                a.remove(repo)
    print (checked)
    print (a)
    return redirect(url_for('go_dash', ending=None))



@app.route('/api/user', defaults={'ending': None})
@app.route('/api/user/<path:ending>')
@login_required
def get_user(ending):
    return user_gen()

@app.route('/api/user/repos', methods=['GET'])
@login_required
def get_userrepo():
    return userrepos_json(g.user)


#
# login part
#

@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('go_dash', ending=None))
    return gh.authorize(callback=url_for('authorized', next=request.args.get('next'), _external=True))


@gh.tokengetter
def get_gh_oauth_token():
    return session.get('github_token')


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = gh.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    # success
    #sss = (resp['access_token'], '')
    str = resp['access_token']
    session['github_token'] = str
    user = getUserData(str,)
    db.updateUserInfo(user)
    login_user(user)
    # if request.args.get('next'):
    #     print(request.args.get('next'))
    #     print(request.args.get('url'))
    # #    return redirect(request.args.get('next'))
    #return redirect(url_for('index', next=request.args.get('next')))
    return redirect(url_for('go_dash', ending=None))


@login_manager.user_loader
def load_user(id):
    if 'github_token' in session:
        return getUserData(session['github_token'])
    return User(id, None, None, None, None)

@login_manager.unauthorized_handler
def unauthorized():
    if request.form.get('url'):
        session['url'] = request.form.get('url')
    return redirect(url_for('login', next=request.endpoint))