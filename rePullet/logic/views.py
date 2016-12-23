from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask import g
from flask_oauthlib.client import OAuth

from rePullet import app
from rePullet.logic import Ins

from flask import render_template

from rePullet.logic.jsongen import *
from github import Github


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
    app_key = 'GITHUB'

)


@app.before_request
def before_request():
    g.user = None
    #print(g.user)
    if 'github_token' in session:
        g.user = session['github_token']
        #print(g.user)

@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user is not None:
        print('hello')
    return render_template('index.html', user=g.user)

@app.route('/dashboard', methods=['GET', 'POST'])
def go_dash():
    if request.form.get('url'):
        session['urlrepo'] = request.form.get('url')
        return redirect(url_for('go_dash'))
    if g.user is None:
        return redirect(url_for('login', next=request.url))
    return render_template('dashboard.html', ddd=session.get('urlrepo'))

@app.route('/api/groups/<urluser>/<urlrepo>',defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/',defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/<ending>')
def get_groups(urluser,urlrepo,ending):
    return group_gen(urluser,urlrepo)

@app.route('/api/items/<urluser>/<urlrepo>',defaults={'ending': None})
@app.route('/api/items/<urluser>/<urlrepo>/',defaults={'ending': None})
@app.route('/api/items/<urluser>/<urlrepo>/<ending>')
def get_items(urluser,urlrepo,ending):
    params = request.args.to_dict()
    return items_gen(urluser,urlrepo,params)


@app.route('/api/options/<urluser>/<urlrepo>',defaults={'ending': None})
@app.route('/api/options/<urluser>/<urlrepo>/',defaults={'ending': None})
@app.route('/api/options/<urluser>/<urlrepo>/<ending>')
def get_options(urluser,urlrepo,ending):
    return options_gen(urluser,urlrepo)

@app.route('/api/user',defaults={'ending': None})
@app.route('/api/user/',defaults={'ending': None})
@app.route('/api/user/<ending>')
def get_user(ending):
    return user_gen();


#
# login part
#


@app.route('/login')
def login():
    return gh.authorize(callback=url_for('authorized', next=request.args.get('next'), _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
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
    #success
    session['github_token'] = (resp['access_token'], '')
    Ins.gt = Github(login_or_token=resp['access_token'])
    print(Ins.gt.get_user())
    print(session['github_token'])
    print(gh.get('user'))
    if request.args.get('next'):
        return redirect(request.args.get('next'))
    return redirect(url_for('index', next=request.args.get('next')))

@gh.tokengetter
def get_gh_oauth_token():
    return session.get('github_token')