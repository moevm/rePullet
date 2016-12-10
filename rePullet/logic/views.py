from urllib.parse import urlparse

from flask import redirect
from flask import request
from flask import session
from flask import url_for

from rePullet import app
from flask import render_template

from rePullet.logic.jsongen import *

@app.route('/', methods=['GET', 'POST'])
def go_new():
    return render_template('index.html')

@app.route('/preview', methods=['GET', 'POST'])
def go_prev():
    if request.form.get('url'):
        session['urlrepo'] = request.form.get('url')
        return redirect(url_for('go_prev'))
    return render_template('preview.html', ddd=session.get('urlrepo'))

@app.route('/api/groups/<urluser>/<urlrepo>',defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/',defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/<ending>')
def get_groups(urluser,urlrepo,ending):
    return group_gen(urluser,urlrepo)

@app.route('/api/items/<urluser>/<urlrepo>',defaults={'ending': None})
@app.route('/api/items/<urluser>/<urlrepo>/',defaults={'ending': None})
@app.route('/api/items/<urluser>/<urlrepo>/<ending>')
def get_items(urluser,urlrepo,ending):
    return items_gen(urluser,urlrepo)