from flask import redirect
from flask import request
from flask import session
from flask import url_for, jsonify

from flask_oauthlib.client import OAuth

from rePullet import app
from flask import render_template

from rePullet.logic.jsongen import *

from config import Config as c


oauth = OAuth(app)

gh_instanse = oauth.remote_app(
    'github',
    consumer_key= c.consumer_key,
    consumer_secret=c.consumer_secret,
    request_token_params= c.scope,
    # consumer_key='a11a1bda412d928fb39a',
    # consumer_secret='92b7cf30bc42c49d589a10372c3f9ff3bb310037',
    # request_token_params={'scope': 'user:email'},
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize'
)

@app.route('/', methods=['GET', 'POST'])
def go_new():
    return render_template('index.html')

@app.route('/preview', methods=['GET', 'POST'])
def go_prev():
    if request.form.get('url'):
        session['urlrepo'] = request.form.get('url')
        return redirect(url_for('go_prev'))
    return render_template('preview.html', ddd=session.get('urlrepo'))

@app.route('/dashboard', methods=['GET', 'POST'])
def go_dash():
    if request.form.get('url'):
        session['urlrepo'] = request.form.get('url')
        return redirect(url_for('go_dash'))
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

#
# login part
#

@app.route('/login')
def login():
    return gh_instanse.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('github_token', None)
    return redirect(url_for('index'))

@app.route('/login/authorized')
def authorized():
    resp = gh_instanse.authorized_response()
    if resp is None or resp.get('access_token') is None:
        return 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
    session['github_token'] = (resp['access_token'], '')
    me = gh_instanse.get('user')
    return jsonify(me.data)

@gh_instanse.tokengetter
def get_gh_instance_oauth_token():
    return session.get('github_token')
