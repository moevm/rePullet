from flask import redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user, current_user
from flask_oauthlib.client import OAuth

from rePullet import app, login_manager
import rePullet.logic.dbcore as db
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


@app.before_request
def before_request():
    g.user = current_user


@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user is not None and g.user.is_authenticated:
        return render_template('index.html', user=g.user)
    else:
        return render_template('index.html', user=None)


@app.route('/guide', methods=['GET', 'POST'])
def guide():
    return render_template('index.html', user=None)

#
# dashboard group
#


@app.route('/dashboard', defaults={'ending': None}, methods=['GET', 'POST'])
#@app.route('/dashboard/', defaults={'ending': None}, methods=['GET', 'POST']) # trailing slash, BITCH
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
    # if request.method == 'POST':
    #     print('that')
    # else:
    #     print('lol')
    if request.form.get('url'): #переход по репозиторию с главной страницы
        print('this')
        repo_name = db.addToTrack(request.form.get('url'), g.user) #добавление репозитория в список отслеживаемых
        #db.printdb()
        return redirect(url_for('go_view', ending=repo_name))
    return render_template('dashboard.html', user=g.user, path=ending)
#
# @app.route('/preview', methods=['GET', 'POST'])
# @login_required
# def go_preview():
#     # TODO: redirect without error window
#     if request.form.get('repoid'):
#         session['repoid'] = request.form.get('repoid')
#         return redirect(url_for('go_preview', ending=None))
#     return render_template('dashboard.html', user=g.user, path='preview')


@app.route('/view/', defaults={'ending': None}, methods=['GET'])
@app.route('/view/<path:ending>', methods=['GET'])
@login_required
def go_view(ending):
    #TODO: complete this function
    print(ending)
    repoid = ending
    if repoid is None:
        return redirect(url_for('go_dash', ending=None))
    #print(repoid)
    return render_template('dashboard.html', user=g.user, path='view', r=repoid)




@app.route('/olddashboard', methods=['GET', 'POST'])
@login_required
def old_dash():
    if request.form.get('url'):
        session['urlrepo'] = request.form.get('url')
        return redirect(url_for('go_dash', ending=None))
    if g.user is None or not g.user.is_authenticated:
        return redirect(url_for('login', next=request.url), code=307)  # POST = 307
    #if is_repo_owner(session['urlrepo'], g.user):
    #    print('success!')
    return render_template('olddashboard.html', ddd=session.get('urlrepo'), user=g.user)


@app.route('/api/groups/<urluser>/<urlrepo>', defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/', defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/<ending>')
def get_groups(urluser, urlrepo, ending):
    return group_gen(urluser, urlrepo)


@app.route('/api/items/<urluser>/<urlrepo>', defaults={'ending': None}, methods=['GET', 'POST'])
@app.route('/api/items/<urluser>/<urlrepo>/', defaults={'ending': None}, methods=['GET', 'POST'])
@app.route('/api/items/<urluser>/<urlrepo>/<ending>', methods=['GET', 'POST'])
def get_items(urluser, urlrepo, ending):
    params = request.args.to_dict()
    # request_data = request.get_json()
    # if (g.user is not None
    #     and g.user.is_authenticated):
    #     db.saveDates(request_data, g.user, urluser, urlrepo)
    return items_gen(urluser, urlrepo, params)


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
    # saveDates(None, g.user, 'G0DZ', 'TPR')
    return user_gen()


@app.route('/api/addrepo', methods=['POST'])
@login_required
def post_addrepo():
    # TODO: Method not allowed
    if request.form.get('url'):
        # добавляем репозиторий к отслеживаемым
        db.addToTrack(request.form.get('url'), g.user)
        return redirect(url_for('go_dash', ending=None))
    return redirect(url_for('go_dash', ending=None))


@app.route('/api/user/repos', methods=['GET'])
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
    user = getUserData(str)
    db.updateUserInfo(user)
    login_user(user)
    #if request.args.get('next'):
    #    return redirect(request.args.get('next'))
    #return redirect(url_for('index', next=request.args.get('next')))
    return redirect(url_for('go_dash', ending=None))


@login_manager.user_loader
def load_user(id):
    if 'github_token' in session:
        return getUserData(session['github_token'])
    return User(id, None, None, None)


