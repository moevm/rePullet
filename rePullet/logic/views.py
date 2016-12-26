from flask import redirect, render_template, request, session, url_for, abort
from flask_login import login_required, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth
import pymongo
from rePullet import app, login_manager
from rePullet.logic.gh import *
from rePullet.logic.jsongen import *
from rePullet.logic import db, db_deadline, db_users
from rePullet.logic.dbcore import *

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


@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user is None:
        print('hello')
    return render_template('index.html', user=g.user)


@app.route('/dashboard', methods=['GET', 'POST'])
def go_dash():
    if request.form.get('url'):
        session['urlrepo'] = request.form.get('url')
        return redirect(url_for('go_dash'))
    if g.user is None or not g.user.is_authenticated:
        return redirect(url_for('login', next=request.url), code=307)  # POST = 307
    return render_template('dashboard.html', ddd=session.get('urlrepo'), user=g.user)


@app.route('/api/groups/<urluser>/<urlrepo>', defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/', defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/<ending>')
def get_groups(urluser, urlrepo, ending):
    return group_gen(urluser, urlrepo)


@app.route('/api/items/<urluser>/<urlrepo>', defaults={'ending': None}, methods=['GET', 'POST'])
@app.route('/api/items/<urluser>/<urlrepo>/', defaults={'ending': None}, methods=['GET', 'POST'])
@app.route('/api/items/<urluser>/<urlrepo>/<ending>', methods=['GET', 'POST'])
def get_items(urluser, urlrepo, ending):
    if not urluser or not urlrepo:
        abort(404)
    params = request.args.to_dict()
    request_data = request.get_json()
    if (g.user is not None
       and g.user.is_authenticated):
        saveDates(request_data, g.user, urluser, urlrepo)
    return items_gen(urluser, urlrepo, params, request_data)


@app.route('/api/options/<urluser>/<urlrepo>', defaults={'ending': None})
@app.route('/api/options/<urluser>/<urlrepo>/', defaults={'ending': None})
@app.route('/api/options/<urluser>/<urlrepo>/<ending>')
def get_options(urluser, urlrepo, ending):
    return options_gen(urluser, urlrepo)


@app.route('/api/user', defaults={'ending': None})
@app.route('/api/user/', defaults={'ending': None})
@app.route('/api/user/<ending>')
@login_required
def get_user(ending):
    #saveDates(None, g.user, 'G0DZ', 'TPR')
    return user_gen()

#
# login part
#


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('get_user'))
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
    session['github_token'] = (resp['access_token'], '')

    str = resp['access_token']
    user = getUserData(str)
    updateUserInfo(user)
    login_user(user)
    # Ins.gt = Github(login_or_token=session['github_token'][0])
    #
    # print(Ins.gt.get_user())
    # print(session['github_token'])
    # print(gh.get('user'))
    if request.args.get('next'):
        return redirect(request.args.get('next'))
    return redirect(url_for('index', next=request.args.get('next')))


@login_manager.user_loader
def load_user(id):
    if 'github_token' in session:
        return getUserData(session['github_token'][0])
    return User(id, None, None)
